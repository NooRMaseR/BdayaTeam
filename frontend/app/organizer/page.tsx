import type { SettingsSiteImageQuery } from "../generated/graphql";
import { GET_SITE_IMAGE_SETTINGS } from "../utils/graphql_helpers";
import NavigationCard from "../components/navigation_card";
import { serverGraphQL } from "../utils/api_utils";
import { API } from "../utils/api.server";
import type { Metadata } from "next";
import ResetAll from "./reset_all";


export async function generateMetadata(): Promise<Metadata> {
    const res = await serverGraphQL<SettingsSiteImageQuery>(GET_SITE_IMAGE_SETTINGS);
    const site = res.data.allSettings?.siteImage;

    return {
        title: "Organizer Team Bdaya",
        description: "Organizer Team Bdaya, Come and manage your everything",
        keywords: "Organizer,organizer,Track,Settings",
        openGraph: {
            title: `Organizer Team Dbaya`,
            description: `Manage tracks members and attendance.`,
            images: site ? [`${process.env.NEXT_PUBLIC_MEDIA_URL}${site}`] : undefined,
        },
    }
}

export default async function OrganizerPage() {
    const { data } = await API.GET("/api/tracks/");

    return (
        <>
            <div className="flex justify-center flex-wrap w-full gap-10 mt-10">
                {data?.map((track) => (
                    <NavigationCard
                        url={`organizer/${track.track}`}
                        title={track.track}
                        desc={track.description ?? ""}
                        imageUrl={track.image ? `${process.env.NEXT_PUBLIC_MEDIA_URL}/${track.image}` : undefined}
                        key={track.id}
                    />
                ))}
                <NavigationCard
                    url="organizer/add-track"
                    title="Add Track"
                    desc="Add Track"
                />
                <NavigationCard
                    url="organizer/settings"
                    title="Site Settings"
                    desc="Edit or view Site settings"
                />
                <NavigationCard
                    url={`${process.env.NEXT_PUBLIC_API_URL}/api/admin/`}
                    title="Admin Site"
                    desc="Open The Main Admin Site"
                />
                <ResetAll />
            </div>
        </>
    )
}
