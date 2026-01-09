import { print } from 'graphql';
import { Metadata } from 'next';
import { gql } from "@apollo/client";
import { API } from "@/app/utils/api.server";
import { serverGraphQL } from "@/app/utils/api_utils";
import MembersGridTable from "@/app/components/member_grid_table";
import { SeeOrganizerCanEditQuery } from '@/app/generated/graphql';
import { AttendanceStatus, MemberStatus } from "@/app/utils/api_types_helper";
import type { GridColDef, GridColumnGroupingModel, GridRowsProp } from '@mui/x-data-grid';


type Props = {
  params: Promise<{ track: string }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { track } = await params;

  return {
    title: `${track} Track Members Dashboard | Organizer`,
    description: `Manage members, attendance, and days for the ${track} track.`,
    
    openGraph: {
      title: `Organizer: ${track} Track Members`,
      description: `Manage ${track} track members and attendance.`,
      images: [`/bdaya_black.png`], 
    },
  };
}


const EDITABLE_FIELDS = gql`
    query SeeOrganizerCanEdit {
        allSettings {
            organizerCanEdit
        }
    }
`;

export default async function OrganizerMembersPage({ params }: Props) {
    const { track } = await params;
    const [tracksRes, daysRes, membersRes, editableFields] = await Promise.all(
        [
            API.GET('/tracks/'),
            API.GET(`/organizer/attendance/{track_name}/days/`, {params: {path: {track_name: track}}}),
            API.GET(`/organizer/members/{track_name}/`, {params: {path: {track_name: track}}}),
            serverGraphQL<SeeOrganizerCanEditQuery>(print(EDITABLE_FIELDS))
        ]
    );
    
    if (!membersRes.response.ok) {
        return <h1>An Error Occured</h1>;
    };

    const rows: GridRowsProp = membersRes.data?.map((member) => {
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
        { align: "center", headerAlign: "center", field: "code", headerName: "Code", editable: editableFields.data.allSettings?.organizerCanEdit.includes("code") },
        { field: "name", headerName: "name", width: 200, editable: editableFields.data.allSettings?.organizerCanEdit.includes("name") },
        { align: "center", headerAlign: "center", field: "status", headerName: "Status", width: 100, editable: editableFields.data.allSettings?.organizerCanEdit.includes("status"), type: 'singleSelect', valueOptions: Object.values(MemberStatus) },
        { align: "center", headerAlign: "center", field: "bonus", headerName: "bonus", editable: editableFields.data.allSettings?.organizerCanEdit.includes("bonus"), type: "number" },
        { align: "center", headerAlign: "center", field: "track", headerName: "track name", editable: editableFields.data.allSettings?.organizerCanEdit.includes("track"), type: "singleSelect", valueOptions: tracksArray },
        { field: "phone", headerName: "phone number", width: 200, editable: editableFields.data.allSettings?.organizerCanEdit.includes("phone") },
        { field: "email", headerName: "email", width: 200, editable: editableFields.data.allSettings?.organizerCanEdit.includes("email") },
        ...(daysRes.data?.flatMap<GridColDef>((day) => {
            const dayName = new Date(day.day).toDateString();
            colorize.push(day.day);
            return [
                {
                    field: `${day.day}_date`,
                    headerName: dayName,
                    width: 170,
                    align: "center",
                    headerAlign: "center",
                    editable: true,
                    type: "singleSelect",
                    valueOptions: Object.values(AttendanceStatus),
                },
                {
                    field: `${day.day}_excuse`,
                    headerName: "Notes",
                    width: 170,
                    headerAlign: "center",
                    editable: true,
                }
            ];
        }) || [])
    ];

    const columnGroupingModel: GridColumnGroupingModel = daysRes.data?.map((day) => ({
        groupId: day.day,
        headerName: new Date(day.day).toLocaleDateString('en-US', { weekday: 'long' }),
        children: [{ field: `${day.day}_date` }, { field: `${day.day}_excuse` }],
        headerAlign: "center"
    })) || [];

    return (
        <MembersGridTable rows={rows} columns={columns} columnGroupingModel={columnGroupingModel} />
    )
}
