import BodyM from '@/app/components/bodyM';
import type { TechnicalParams } from '../page';
import MembersGridTable from '@/app/components/member_grid_table';
import { getMemberGrid } from '@/app/[locale]/organizer/[track]/members/page';

import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';

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
    <BodyM>
      <MembersGridTable rows={rows} columns={columns} columnGroupingModel={groupModel} track={track} />
    </BodyM>
  )
}
