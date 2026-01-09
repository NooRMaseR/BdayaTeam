import TrackCard from "../components/track_card";
import { API } from "../utils/api.server";
import { Metadata } from "next";

export const metadata: Metadata = {
    title: "Organizer Team Bdaya",
    description: "Organizer Team Bdaya, Come and manage your everything",
    keywords: "Organizer,organizer,Track,Settings",
    openGraph: {
        title: `Organizer Team Dbaya`,
        description: `Manage tracks members and attendance.`,
        images: [`/bdaya_black.png`],
    },
}

export default async function OrganizerPage() {
    const { data } = await API.GET("/tracks/", { next: { revalidate: 300 } });

    return (
        <>
            <div className="flex justify-center flex-wrap w-full gap-10">
                {data?.map((track) => (
                    <TrackCard
                        url={`organizer/${track.track}`}
                        title={track.track}
                        desc={track.description ?? ""}
                        key={track.id}
                    />
                ))}
                <TrackCard
                    url="organizer/add-track"
                    title="Add Track"
                    desc="Add Track"
                />
                <TrackCard
                    url="organizer/settings"
                    title="Site Settings"
                    desc="Edit or view Site settings"
                />
            </div>
        </>
    )
}
