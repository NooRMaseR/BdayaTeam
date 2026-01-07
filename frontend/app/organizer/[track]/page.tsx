import TrackCard from "@/app/components/track_card";
import { Metadata } from "next";

type Props = {
  params: Promise<{ track: string }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { track } = await params;

  return {
    title: `${track} Track Dashboard | Organizer`,
    description: `Manage members, attendance, and days for the ${track} track.`,
    
    openGraph: {
      title: `Organizer: ${track} Track`,
      description: `Manage ${track} track members and attendance.`,
      images: [`/bdaya_black.png`], 
    },
  };
}


export default async function OrganizerTrackPage({params}: Props) {
  const {track} = await params;
  return (
    <div className="flex justify-center flex-wrap gap-6 mt-4">
      <TrackCard
          url={`${track}/members`}
          title="See Members"
          desc="See members of these tracks and Take attendances or update somthing"
      />
      <TrackCard
          url={`${track}/days`}
          title="See Track Days"
          desc="See Track Days to add attendance day or update one"
      />
    </div>
  )
}
