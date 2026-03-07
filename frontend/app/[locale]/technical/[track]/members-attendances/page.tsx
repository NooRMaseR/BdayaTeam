import BodyM from '@/app/components/bodyM';
import type { TechnicalParams } from '../page';
import MembersGridTable from '@/app/components/member_grid_table';

import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import { getOrgMemberGrid } from "@/app/[locale]/organizer/[track]/members/page";


export default async function MembersPage({ params }: TechnicalParams) {
  const { track } = await params;
  let rows, columns, groupModel;
  try {
    ({ rows, columns, groupModel } = await getOrgMemberGrid(track, true));
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
