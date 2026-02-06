import type { Metadata } from 'next';
import Chip from '@mui/material/Chip';
import BodyM from '@/app/components/bodyM';
import { API } from '../../../utils/api.server';
import { getTranslations } from 'next-intl/server';
import { serverGraphQL } from '@/app/utils/api_utils';
import { GET_SITE_IMAGE_SETTINGS } from '@/app/utils/graphql_helpers';
import type { SettingsSiteImageQuery } from '@/app/generated/graphql';


export async function generateMetadata(): Promise<Metadata> {
    const [tr, res] = await Promise.all(
        [
            getTranslations('profilePage'),
            serverGraphQL<SettingsSiteImageQuery>(GET_SITE_IMAGE_SETTINGS)
        ]
    );
    const site = res.data.allSettings?.siteImage;

    return {
        title: tr('metaTitle'),
        description: tr('metaDesc'),
        robots: {
            index: false,
            follow: false
        },
        openGraph: {
            title: tr('metaTitle'),
            description: tr('metaDesc'),
            images: site ? [`${process.env.NEXT_PUBLIC_API_URL}${process.env.NEXT_PUBLIC_MEDIA_URL}${site}`] : undefined,
        },
    }
}

type ParamsProps = {
    params: Promise<{ code: `${string}-${number}` }>;
}

function Stat({ label, value }: { label: string; value: number | string }) {
    return (
        <div className="flex-1 bg-slate-50 p-3 rounded-lg text-center">
            <div className="text-lg font-semibold text-slate-900">{value}</div>
            <div className="mt-1 text-xs text-slate-500">{label}</div>
        </div>
    )
}

export default async function ProfilePage({ params }: ParamsProps) {
    const [tr, { code }] = await Promise.all(
        [
            getTranslations('profilePage'),
            params
        ]
    );
    const { response, data } = await API.GET("/api/member/profile/{member_code}/", { params: { path: { member_code: code } } });
    const user = response.ok && data ? data : null;

    if (!user) {
        return (
            <BodyM>
                <div className="min-h-screen flex items-center justify-center p-8 bg-linear-to-br from-sky-50 via-emerald-50 to-rose-50">
                    <div className="w-full max-w-3xl bg-white/60 backdrop-blur-sm border border-slate-100/50 rounded-xl p-8 shadow-lg">
                        <h2 className="text-xl font-semibold text-slate-900">{tr('profile')}</h2>
                        <p className="mt-3 text-slate-500">{tr('error')}</p>
                    </div>
                </div>
            </BodyM>
        )
    }

    return (
        <div className="min-h-screen flex justify-center w-full bg-linear-to-br from-blue-400 via-green-400 to-rose-50">
            <section className="w-full bg-white/70 backdrop-blur-sm rounded-xl shadow-md border-slate-100/50">
                <BodyM>
                    <div className="flex items-center gap-4 mb-4 p-4 bg-blue-300 h-40">
                        <div className="w-18 h-18 flex items-center justify-center rounded-full bg-linear-to-br from-sky-500 to-emerald-400 text-white font-bold text-2xl">
                            {user.name[0].toUpperCase()}
                        </div>
                        <div className='flex flex-col gap-4'>
                            <h1 className="text-2xl font-semibold text-slate-900 mt-8">{user.name}</h1>
                            <div className='flex gap-3'>
                                <Chip label={tr('track', { name: user.track.track })} color='info' />
                                <Chip label={tr('code', { code: user.code || '' })} color='info' />
                            </div>
                        </div>
                    </div>
                    <div className="flex gap-3 mt-4 flex-col p-4 sm:flex-row">
                        <Stat label={tr("abs")} value={user.absents} />
                        <Stat label={tr("sent")} value={user.total_tasks_sent} />
                        <Stat label={tr("missing")} value={user.missing_tasks} />
                    </div>
                </BodyM>
            </section>
        </div>
    )
}
