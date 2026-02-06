import type { Metadata } from "next";
import BodyM from "@/app/components/bodyM";
import SeeProfileCard from "./see_profile_card";
import { getTranslations } from "next-intl/server";
import { serverGraphQL } from "@/app/utils/api_utils";
import NavigationCard from "../../../components/navigation_card";
import { GET_SITE_IMAGE_SETTINGS } from "@/app/utils/graphql_helpers";
import type { SettingsSiteImageQuery } from "@/app/generated/graphql";

export async function generateMetadata(): Promise<Metadata> {
  const [tr, res] = await Promise.all(
    [
      getTranslations('technicalPage'),
      serverGraphQL<SettingsSiteImageQuery>(GET_SITE_IMAGE_SETTINGS)
    ]
  );
  const site = res.data.allSettings?.siteImage;

  return {
    title: tr('metaTitle'),
    description: tr('metaDesc'),
    keywords: tr('metaKeys'),
    openGraph: {
      title: tr('metaTitle'),
      description: tr('metaDesc'),
      images: site ? [`${process.env.NEXT_PUBLIC_MEDIA_URL}${site}`] : undefined,
    },
  }
}

export type TechnicalParams = {
  params: Promise<{ track: string }>
}

export default async function TechnicalPage({ params }: TechnicalParams) {
  const [tr, { track }] = await Promise.all(
    [
      getTranslations("technicalPage"),
      params
    ]
  );
  return (
    <BodyM>
      <div className="flex justify-center items-center min-h-[calc(100vh-105px)] flex-wrap gap-6">
        <NavigationCard
          url={`${track}/tasks`}
          title={tr('tasks')}
          desc={tr('tasksDesc')}
        />
        <NavigationCard
          url={`${track}/members`}
          title={tr('members')}
          desc={tr('membersDesc')}
        />
        <SeeProfileCard />
      </div>
    </BodyM>
  );
}
