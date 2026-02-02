import type { Get_Member_CodeQuery, SettingsSiteImageQuery } from '@/app/generated/graphql';
import { GET_MEMBER_CODE, GET_SITE_IMAGE_SETTINGS } from '@/app/utils/graphql_helpers';
import NavigationCard from '@/app/components/navigation_card';
import { serverGraphQL } from '@/app/utils/api_utils';
import type { Metadata } from 'next';

export type ParamsProps = {
    params: Promise<{ trackName: string }>
};

export async function generateMetadata(): Promise<Metadata> {
    const res = await serverGraphQL<SettingsSiteImageQuery>(GET_SITE_IMAGE_SETTINGS);
    const site = res.data.allSettings?.siteImage;

    return {
        title: "Member Team Bdaya",
        description: "Member Team Bdaya, Come and manage your tasks to get bonus and win a certificate",
        keywords: "Member,member,Tasks,Profile,Task",
        openGraph: {
            title: `Member Team Bdaya`,
            description: `Learn, Solve Tasks to get bonus.`,
            images: site ? [`${process.env.NEXT_PUBLIC_MEDIA_URL}${site}`] : undefined,
        },
    }
}


export default async function MemberTrackPage({ params }: ParamsProps ) {
    const [paramsPromise, codeRes ] = await Promise.all(
        [
            params,
            serverGraphQL<Get_Member_CodeQuery>(GET_MEMBER_CODE)
        ]
    );
    const trackName = paramsPromise.trackName.replaceAll("%20", ' ');
    return (
        <>
            <div className="flex justify-center flex-wrap w-full gap-10 mt-10">
                <NavigationCard
                    url={`/profile/${codeRes.data.member?.code}`}
                    title="Profile"
                    desc="See Your Profile"
                />
                <NavigationCard
                    url={`${trackName}/tasks`}
                    title="See Tasks"
                    desc="See Your Track Tasks"
                />
            </div>
        </>
    );
}
