import API from "@/app/utils/api.server";
import BodyM from '@/app/components/bodyM';
import type { TechnicalParams } from '../page';
import { getTranslations } from 'next-intl/server';
import MembersGridTable from '@/app/components/member_grid_table';
import { type GetMemberGridType, MemberStatus } from "@/app/utils/api_types_helper";
import type { GridColDef, GridColumnGroupingModel, GridRowsProp } from '@mui/x-data-grid';

import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';

async function getTechMemberGrid(track: string): Promise<GetMemberGridType> {
  const [tr, membersRes, tasksRes] = await Promise.all(
    [
      getTranslations('showMembersPage'),
      API.GET(`/api/technical/members/{track_name}/with-tasks/`, { params: { path: { track_name: track } } }),
      API.GET('/api/technical/tasks/')
    ]
  );
  
  if (!membersRes.response.ok) {
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
      track: member.track.name,
      phone: member.phone_number,
      email: member.email,
    };

    member.tasks.forEach(recived_task => {
      row[`task_deg_${recived_task.task.id}`] = recived_task.degree;
      row[`task_notes_${recived_task.task.id}`] = recived_task.technical_notes;
      row[`task_signed_by_${recived_task.task.id}`] = recived_task.signed_by?.username;
    });

    return row;
  }) || [];

  const columns: GridColDef[] = [
    { align: "center", headerAlign: "center", field: "code", headerName: tr("code") }, // cellClassName: 'sticky left-0 z-3 bg-white'
    { field: "name", headerName: tr("name"), width: 200 },
    { align: "center", headerAlign: "center", field: "status", headerName: tr("status"), width: 100, type: 'singleSelect', valueOptions: Object.values(MemberStatus).map((status) => ({ label: tr(status), value: status })) },
    { align: "center", headerAlign: "center", field: "bonus", headerName: tr("bonus"), type: "number" },
    { align: "center", headerAlign: "center", field: "track", headerName: tr("trackName") },
    { field: "phone", headerName: tr("phone"), width: 200 },
    { field: "email", headerName: tr("email"), width: 200 },
    ...(tasksRes.data?.flatMap<GridColDef>((task) => {
      return [
        {
          field: `task_deg_${task.id}`,
          headerName: tr("degree"),
          width: 80,
          align: "center",
          headerAlign: "center",
          type: "number",
          filterable: false,
          editable: true
        },
        {
          field: `task_notes_${task.id}`,
          headerName: tr('notes'),
          width: 170,
          align: "center",
          headerAlign: "center",
          filterable: false,
          sortable: false,
          editable: true
        },
        {
          field: `task_signed_by_${task.id}`,
          headerName: tr('signed_by'),
          width: 170,
          align: "center",
          headerAlign: "center",
          filterable: false,
          sortable: false,
          editable: false
        }
      ];
    }) || [])
  ];

  const columnGroupingModel: GridColumnGroupingModel = tasksRes.data?.map((task) => ({
    groupId: task.id.toString(),
    headerName: tr('task', {number: task.task_number}),
    children: [{ field: `task_deg_${task.id}` }, { field: `task_notes_${task.id}` }, { field: `task_signed_by_${task.id}` }],
    headerAlign: "center",
  })) || [];
  
  return {
    rows: rows,
    columns: columns,
    groupModel: columnGroupingModel
  }
}


export default async function MembersPage({ params }: TechnicalParams) {
  const { track } = await params;
  let rows, columns, groupModel;
  try {
    ({ rows, columns, groupModel } = await getTechMemberGrid(track));
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
      <MembersGridTable rows={rows} columns={columns} columnGroupingModel={groupModel} track={track} forTech />
    </BodyM>
  )
}
