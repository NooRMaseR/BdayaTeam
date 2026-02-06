import type { Get_Member_CodeQuery, SettingsSiteImageQuery } from '@/app/generated/graphql';
import { GET_MEMBER_CODE, GET_SITE_IMAGE_SETTINGS } from '@/app/utils/graphql_helpers';
import NavigationCard from '@/app/components/navigation_card';
import { serverGraphQL } from '@/app/utils/api_utils';
import { getTranslations } from 'next-intl/server';
import BodyM from '@/app/components/bodyM';
import type { Metadata } from 'next';

export type ParamsProps = {
    params: Promise<{ trackName: string }>
};

export async function generateMetadata(): Promise<Metadata> {
    const [tr, res] = await Promise.all(
        [
            getTranslations('membersPage'),
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


export default async function MemberTrackPage({ params }: ParamsProps ) {
    const [tr, paramsPromise, codeRes ] = await Promise.all(
        [
            getTranslations('membersPage'),
            params,
            serverGraphQL<Get_Member_CodeQuery>(GET_MEMBER_CODE)
        ]
    );
    const trackName = paramsPromise.trackName.replaceAll("%20", ' ');
    return (
        <BodyM>
            <div className="flex justify-center items-center min-h-[calc(100vh-105px)] flex-wrap gap-6">
                <NavigationCard
                    url={`/profile/${codeRes.data.member?.code}`}
                    title={tr('profile')}
                    desc={tr('profileDesc')}
                />
                <NavigationCard
                    url={`${trackName}/tasks`}
                    title={tr('tasks')}
                    desc={tr('tasksDesc')}
                />
            </div>
        </BodyM>
    );
}
