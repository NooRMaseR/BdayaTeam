import type { TechnicalParams } from '../page';
import MembersGridTable from '@/app/components/member_grid_table';
import { getMemberGrid } from '@/app/organizer/[track]/members/page';
import { Dialog, DialogContent, DialogContentText, DialogTitle } from '@mui/material';

export default async function MembersPage({ params }: TechnicalParams) {
  const { track } = await params;
  let rows, columns, groupModel;
  try {
    ({ rows, columns, groupModel } = await getMemberGrid(track));
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } catch (e: any) {
    return <Dialog open>
      <DialogTitle>Opps!!</DialogTitle>
      <DialogContent>
        <DialogContentText>{e?.details || 'error occured' }</DialogContentText>
      </DialogContent>
    </Dialog>
  };

  return (
    <MembersGridTable rows={rows} columns={columns} columnGroupingModel={groupModel} track={track} />
  )
}
