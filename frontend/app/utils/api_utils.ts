/* eslint-disable @typescript-eslint/no-explicit-any */
'use server';

import type { SeeOrganizerCanEditQuery } from "../generated/graphql";
import { AttendanceStatus, MemberStatus, type GetMemberGridType } from "./api_types_helper";
import type { GridColDef, GridColumnGroupingModel, GridRowsProp } from "@mui/x-data-grid";
import { EDITABLE_FIELDS } from "./graphql_helpers";
import { getAuthCookies, serverGraphQL } from "./gql_applolo";
import { getTranslations } from "next-intl/server";
import API, { fetchTracks } from "./api.server";
import { revalidateTag } from "next/cache";
import { cookies } from "next/headers";

function parseCookie(cookie: string) {
    const splited = cookie.split(";").map((value) => value.trim());
    const [nameVal, ...attributes] = splited;
    const [name, ...valueParts] = nameVal.split('=');
    const value = valueParts.join('=');

    if (!name || !value) return null;

    const cookieOptions: any = {
        name: name,
        value: value,
        path: '/',
    };
    attributes.forEach(attr => {
        const lowerAttr = attr.toLowerCase();

        if (lowerAttr === 'httponly') {
            cookieOptions.httpOnly = true;
        } else if (lowerAttr === 'secure') {
            cookieOptions.secure = true;
        } else if (lowerAttr.startsWith('samesite=')) {
            const sameSiteVal = attr.split('=')[1].toLowerCase();
            if (['lax', 'strict', 'none'].includes(sameSiteVal)) {
                cookieOptions.sameSite = sameSiteVal as 'lax' | 'strict' | 'none';
            }
        } else if (lowerAttr.startsWith('max-age=')) {
            cookieOptions.maxAge = parseInt(attr.split('=')[1]);
        } else if (lowerAttr.startsWith('expires=')) {
            const dateStr = attr.split('=')[1];
            cookieOptions.expires = new Date(dateStr).getTime();
        } else if (lowerAttr.startsWith('path=')) {
            cookieOptions.path = attr.split('=')[1];
        }
    });
    return cookieOptions;
}

export const fetchWithCookies = async (url: string | URL | Request, options?: RequestInit): Promise<Response> => {
    const cookieStore = await cookies();
    const { token, csrf, locale } = await getAuthCookies();

    const headers = new Headers(options?.headers);
    if (!headers.get("Content-Type")) {
        headers.set("Content-Type", "application/json");
    }

    const cookieString = cookieStore.getAll().map(c => `${c.name}=${c.value}`).join('; ');
    if (cookieString) {
        headers.set("Cookie", cookieString);
    }

    if (token) {
        headers.set("Authorization", `Bearer ${token}`);
    }

    if (csrf) {
        headers.set("X-CSRFToken", csrf);
    }

    if (locale) {
        headers.set("Accept-Language", locale);
    }

    const response = await fetch(url, {
        ...options,
        headers,
        credentials: "include",
    });

    const setCookieHeaders = response.headers.getSetCookie();
    if (setCookieHeaders && setCookieHeaders.length > 0) {
        setCookieHeaders.forEach((cookieStr) => {
            const parsed = parseCookie(cookieStr);
            if (parsed) {
                try {
                    cookieStore.set(parsed.name, parsed.value, parsed);
                } catch {}
            }
        });
    }

    return response;
};

export async function revalidateTagName(tag: string) {
    revalidateTag(tag, 'max');
}

export async function revalidateTracks() {
    await revalidateTagName("tracks");
}

export async function getOrgMemberGrid(track: string, safe: boolean = false): Promise<GetMemberGridType> {
    const [tr, dtr, membersRes, daysRes, tracksRes, editableFields] = await Promise.all(
        [
            getTranslations('showMembersPage'),
            getTranslations('weekDays'),
            API.GET(`/api/organizer/members/{track_name}/`, { params: { path: { track_name: track } } }),
            API.GET(`/api/organizer/attendance/{track_name}/days/`, { params: { path: { track_name: track } } }),
            fetchTracks(),
            !safe ? serverGraphQL<SeeOrganizerCanEditQuery>(EDITABLE_FIELDS) : { data: { allSettings: { organizerCanEdit: [] as string[] } } }
        ]
    );

    if (!membersRes.response.ok) {
        return Promise.reject(membersRes.error);
    };
    

    const rows: GridRowsProp = (membersRes.data as unknown as (typeof membersRes.data)[])?.map((member) => {
        const row: any = {
            id: member?.code,
            code: member?.code,
            status: member?.status,
            name: member?.name,
            bonus: member?.bonus,
            track: member?.track.name,
            phone: member?.phone_number,
            email: member?.email,
        };

        member?.attendances?.forEach(att => {
            row[`${att.date.day}_date`] = att.status;
            row[`${att.date.day}_excuse`] = att.excuse_reason;
            row[`${att.date.day}_by`] = att.by.username;
        });

        return row;
    }) || [];

    const tracksNameArray: string[] = tracksRes.data?.map((track) => track.name) || [];

    const columns: GridColDef[] = [
        { align: "center", headerAlign: "center", field: "code", headerName: tr("code"), editable: false, pinnable: true, cellClassName: 'sticky left-0 z-3 dark:bg-(--dark-color) bg-white' },
        { field: "name", headerName: tr("name"), width: 200, editable: editableFields.data.allSettings?.organizerCanEdit.includes("name") },
        { align: "center", headerAlign: "center", field: "status", headerName: tr("status"), width: 100, editable: editableFields.data.allSettings?.organizerCanEdit.includes("status"), type: 'singleSelect', valueOptions: Object.values(MemberStatus).map((status) => ({ label: tr(status), value: status })) },
        { align: "center", headerAlign: "center", field: "bonus", headerName: tr("bonus"), editable: editableFields.data.allSettings?.organizerCanEdit.includes("bonus"), type: "number" },
        { align: "center", headerAlign: "center", field: "track", headerName: tr("trackName"), editable: editableFields.data.allSettings?.organizerCanEdit.includes("track"), type: "singleSelect", valueOptions: tracksNameArray },
        { field: "phone", headerName: tr("phone"), width: 200, editable: editableFields.data.allSettings?.organizerCanEdit.includes("phone") },
        { field: "email", headerName: tr("email"), width: 200, editable: editableFields.data.allSettings?.organizerCanEdit.includes("email") },
        ...(daysRes.data?.flatMap<GridColDef>((day) => {
            const dayName = new Date(day.day).toLocaleDateString();
            return [
                {
                    field: `${day.day}_date`,
                    headerName: dayName,
                    width: 170,
                    align: "center",
                    headerAlign: "center",
                    filterable: false,
                    editable: !safe,
                    type: "singleSelect",
                    valueOptions: Object.values(AttendanceStatus).map(status => ({label: tr(status), value: status})),
                },
                {
                    field: `${day.day}_excuse`,
                    headerName: tr("notes"),
                    width: 170,
                    headerAlign: "center",
                    filterable: false,
                    editable: !safe
                },
                {
                    field: `${day.day}_by`,
                    headerName: tr("by"),
                    width: 170,
                    align: "center",
                    headerAlign: "center",
                    filterable: false,
                    editable: false
                }
            ];
        }) || [])
    ];

    const columnGroupingModel: GridColumnGroupingModel = daysRes.data?.map((day) => ({
        groupId: day.day,
        headerName: dtr(new Date(day.day).toLocaleDateString('en-US', { weekday: 'long' })),
        children: [{ field: `${day.day}_date` }, { field: `${day.day}_excuse` }, { field: `${day.day}_by` }],
        headerAlign: "center",
    })) || [];

    return {
        rows: rows,
        columns: columns,
        groupModel: columnGroupingModel
    }
}