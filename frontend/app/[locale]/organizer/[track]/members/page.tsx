import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';

import type { Metadata } from 'next';
import BodyM from '@/app/components/bodyM';
import { serverGraphQL } from '@/app/utils/gql_applolo';
import { getOrgMemberGrid } from "@/app/utils/api_utils";
import { GET_TRACK_IMAGE } from '@/app/utils/graphql_helpers';
import MembersGridTable from "@/app/components/member_grid_table";
import type { Get_Track_ImageQuery } from '@/app/generated/graphql';


type Props = {
    params: Promise<{ track: string }>;
};

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

export default async function OrganizerMembersPage({ params }: Props) {
    const { track } = await params;
    let rows, columns, groupModel;
    try {
        ({ rows, columns, groupModel } = await getOrgMemberGrid(track));
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (e: any) {
        console.error("error", e);
        return <Dialog open>
            <DialogTitle>Opps!!</DialogTitle>
            <DialogContent>
                <DialogContentText>{e?.details || 'error occured'}</DialogContentText>
            </DialogContent>
        </Dialog>
    };
    return (
        <BodyM>
            <MembersGridTable rows={rows} columns={columns} columnGroupingModel={groupModel} track={track} />
        </BodyM>
    )
}
