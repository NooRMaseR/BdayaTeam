import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';

import type { Metadata } from 'next';
import BodyM from '@/app/components/bodyM';
import { API } from "@/app/utils/api.server";
import { getTranslations } from 'next-intl/server';
import { serverGraphQL } from "@/app/utils/api_utils";
import MembersGridTable from "@/app/components/member_grid_table";
import { AttendanceStatus, MemberStatus } from "@/app/utils/api_types_helper";
import { EDITABLE_FIELDS, GET_TRACK_IMAGE } from '@/app/utils/graphql_helpers';
import type { GridColDef, GridColumnGroupingModel, GridRowsProp } from '@mui/x-data-grid';
import type { Get_Track_ImageQuery, SeeOrganizerCanEditQuery } from '@/app/generated/graphql';


type Props = {
    params: Promise<{ track: string }>;
};

type GetMemberGridType = {
    rows: GridRowsProp,
    columns: GridColDef[],
    groupModel: GridColumnGroupingModel
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const { track } = await params;
    const readableTrack = track.replaceAll("%20", ' ');
    const res = await serverGraphQL<Get_Track_ImageQuery>(GET_TRACK_IMAGE, { track: track });
    const trackImage = res.data.track?.image;

    return {
        title: `${readableTrack} Track Members`,
        description: `Manage members, attendance, and days for the ${readableTrack} track.`,

        openGraph: {
            title: `${readableTrack} Track Members`,
            description: `Manage ${readableTrack} track members and attendance.`,
            images: trackImage ? [`${process.env.NEXT_PUBLIC_MEDIA_URL}${trackImage}`] : undefined,
        },
    };
}

export async function getMemberGrid(track: string, editable: boolean = false): Promise<GetMemberGridType> {
    const [tr, dtr, tracksRes, daysRes, membersRes, editableFields] = await Promise.all(
        [
            getTranslations('showMembersPage'),
            getTranslations('weekDays'),
            API.GET('/api/tracks/'),
            API.GET(`/api/organizer/attendance/{track_name}/days/`, { params: { path: { track_name: track } } }),
            API.GET(`/api/organizer/members/{track_name}/`, { params: { path: { track_name: track } } }),
            editable ? serverGraphQL<SeeOrganizerCanEditQuery>(EDITABLE_FIELDS) : Promise.resolve({ data: { allSettings: { organizerCanEdit: [] as string[] } } })
        ]
    );
    
    if (!membersRes.response.ok) {
        console.log(membersRes.error);
        return Promise.reject(membersRes.error);
    };

    const rows: GridRowsProp = membersRes.data?.map((member) => {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const row: any = {
            id: member.code,
            code: member.code,
            status: member.status,
            name: member.name,
            bonus: member.bonus,
            track: member.track.track,
            phone: member.phone_number,
            email: member.email,
        };

        member.attendances.forEach(att => {
            row[`${att.date.day}_date`] = att.status;
            row[`${att.date.day}_excuse`] = att.excuse_reason;
        });
        return row;
    }) || [];

    const colorize: string[] = [];
    const tracksArray: string[] = tracksRes.data?.map((track) => track.track) || [];

    const columns: GridColDef[] = [
        { align: "center", headerAlign: "center", field: "code", headerName: tr("code"), editable: editable && editableFields.data.allSettings?.organizerCanEdit.includes("code"), pinnable: true },
        { field: "name", headerName: tr("name"), width: 200, editable: editable && editableFields.data.allSettings?.organizerCanEdit.includes("name") },
        { align: "center", headerAlign: "center", field: "status", headerName: tr("status"), width: 100, editable: editable && editableFields.data.allSettings?.organizerCanEdit.includes("status"), type: 'singleSelect', valueOptions: Object.values(MemberStatus) },
        { align: "center", headerAlign: "center", field: "bonus", headerName: tr("bonus"), editable: editable && editableFields.data.allSettings?.organizerCanEdit.includes("bonus"), type: "number" },
        { align: "center", headerAlign: "center", field: "track", headerName: tr("trackName"), editable: editable && editableFields.data.allSettings?.organizerCanEdit.includes("track"), type: "singleSelect", valueOptions: tracksArray },
        { field: "phone", headerName: tr("phone"), width: 200, editable: editable && editableFields.data.allSettings?.organizerCanEdit.includes("phone") },
        { field: "email", headerName: tr("email"), width: 200, editable: editable && editableFields.data.allSettings?.organizerCanEdit.includes("email") },
        ...(daysRes.data?.flatMap<GridColDef>((day) => {
            const dayName = new Date(day.day).toLocaleDateString();
            colorize.push(day.day);
            return [
                {
                    field: `${day.day}_date`,
                    headerName: dayName,
                    width: 170,
                    align: "center",
                    headerAlign: "center",
                    editable: editable,
                    filterable: false,
                    type: "singleSelect",
                    valueOptions: Object.values(AttendanceStatus),
                },
                {
                    field: `${day.day}_excuse`,
                    headerName: tr("notes"),
                    width: 170,
                    headerAlign: "center",
                    editable: true,
                    filterable: false
                }
            ];
        }) || [])
    ];

    const columnGroupingModel: GridColumnGroupingModel = daysRes.data?.map((day) => ({
        groupId: day.day,
        headerName: dtr(new Date(day.day).toLocaleDateString('en-US', { weekday: 'long' })),
        children: [{ field: `${day.day}_date` }, { field: `${day.day}_excuse` }],
        headerAlign: "center",
    })) || [];

    return {
        rows: rows,
        columns: columns,
        groupModel: columnGroupingModel
    }
}

export default async function OrganizerMembersPage({ params }: Props) {
    const { track } = await params;
    let rows, columns, groupModel;
    try {
        ({ rows, columns, groupModel } = await getMemberGrid(track, true));
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (e: any) {
        return <Dialog open>
            <DialogTitle>Opps!!</DialogTitle>
            <DialogContent>
                <DialogContentText>{e?.details || 'error occured'}</DialogContentText>
            </DialogContent>
        </Dialog>
    };
    return (
        <BodyM>
            <MembersGridTable rows={rows} columns={columns} columnGroupingModel={groupModel} track={track.replaceAll("%20", ' ')} />
        </BodyM>
    )
}
