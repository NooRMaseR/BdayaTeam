import type { Get_Track_ImageQuery } from "@/app/generated/graphql";
import { GET_TRACK_IMAGE } from "@/app/utils/graphql_helpers";
import { serverGraphQL } from "@/app/utils/api_utils";
import NavigationCard from "@/app/components/navigation_card";
import DeleteTrack from "./delete-track";
import type { Metadata } from "next";

type Props = {
  params: Promise<{ track: string }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { track } = await params;
  const readableTrack = track.replaceAll("%20", ' ');

  const trackRes = await serverGraphQL<Get_Track_ImageQuery>(GET_TRACK_IMAGE, { track: readableTrack });
  let imageUrl: string | undefined;
  if (trackRes.success) {
    imageUrl = `${process.env.NEXT_PUBLIC_MEDIA_URL}${trackRes.data.track?.image}`;
  }

  return {
    title: `${readableTrack} Track Dashboard | Organizer`,
    description: `Manage members, attendance, and days for the ${readableTrack} track.`,
    
    openGraph: {
      title: `Organizer: ${readableTrack} Track`,
      description: `Manage ${readableTrack} track members and attendance.`,
      images: imageUrl ? [imageUrl] : undefined, 
    },
  };
}


export default async function OrganizerTrackPage({params}: Props) {
  const { track } = await params;
  const readableTrack = track.replaceAll("%20", ' ');

  return (
    <div className="flex justify-center flex-wrap gap-6 mt-4">
      <NavigationCard
          url={`${track}/members`}
          title="See Members"
          desc="See members of these tracks and Take attendances or update somthing"
      />
      <NavigationCard
          url={`${track}/days`}
          title="See Track Days"
          desc="See Track Days to add attendance day or update one"
      />
      <DeleteTrack name={readableTrack} />
    </div>
  )
}
