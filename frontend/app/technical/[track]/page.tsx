import type { Metadata } from "next";
import { serverGraphQL } from "@/app/utils/api_utils";
import NavigationCard from "../../components/navigation_card";
import { SettingsSiteImageQuery } from "@/app/generated/graphql";
import { GET_SITE_IMAGE_SETTINGS } from "@/app/utils/graphql_helpers";
import SeeProfileCard from "./see_profile_card";

export async function generateMetadata(): Promise<Metadata> {
  const res = await serverGraphQL<SettingsSiteImageQuery>(GET_SITE_IMAGE_SETTINGS);
  const site = res.data.allSettings?.siteImage;

  return {
    title: "Technical Team Bdaya",
    description: "Technical Team Bdaya, Come and manage your members tasks and create some tasks for them",
    keywords: "Technical,technical,Tasks,Members,Profile",
    openGraph: {
      title: `Technical Team Bdaya:`,
      description: 'Technical Team Bdaya, Come and manage your members tasks and create some tasks for them',
      images: site ? [`${process.env.NEXT_PUBLIC_MEDIA_URL}${site}`] : undefined,
    },
  }
}

export type TechnicalParams = {
  params: Promise<{ track: string }>
}

export default async function TechnicalPage({ params }: TechnicalParams) {
  const { track } = await params;
  return (
    <main className="w-full flex gap-6 justify-center flex-wrap mt-10">
      <NavigationCard
        url={`${track}/tasks`}
        title="See Tasks"
        desc="See Track Tasks and manage them"
      />
      <NavigationCard
        url={`${track}/members`}
        title="See members"
        desc="See Track members"
      />
      <SeeProfileCard />
    </main>
  );
}
