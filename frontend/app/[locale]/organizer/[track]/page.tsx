import type { Get_Track_ImageQuery } from "@/app/generated/graphql";
import NavigationCard from "@/app/components/navigation_card";
import { GET_TRACK_IMAGE } from "@/app/utils/graphql_helpers";
import { serverGraphQL } from "@/app/utils/api_utils";
import { getTranslations } from "next-intl/server";
import BodyM from "@/app/components/bodyM";
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
  const [{ track }, tr] = await Promise.all(
    [
      params,
      getTranslations("trackPage")
    ]
  );
  const readableTrack = track.replaceAll("%20", ' ');

  return (
    <BodyM>
      <div className="flex justify-center items-center min-h-[calc(100vh-105px)] flex-wrap gap-6">
        <NavigationCard
            url={`${track}/members`}
            title={tr('members')}
            desc={tr('membersDesc')}
        />
        <NavigationCard
            url={`${track}/days`}
            title={tr('days')}
            desc={tr('daysDesc')}
        />
        <DeleteTrack name={readableTrack} />
      </div>
    </BodyM>
  )
}
