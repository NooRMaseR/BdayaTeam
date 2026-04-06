import Chip from '@mui/material/Chip';
import Paper from '@mui/material/Paper';
import Avatar from '@mui/material/Avatar';
import Divider from '@mui/material/Divider';
import Typography from '@mui/material/Typography';

import type { Metadata } from 'next';
import MemberTasks from './member_tasks';
import BodyM from '@/app/components/bodyM';
import API from '../../../utils/api.server';
import { getTranslations } from 'next-intl/server';
import { fetchSiteImage } from '@/app/utils/api_utils';

export async function generateMetadata(): Promise<Metadata> {
    const [tr, res] = await Promise.all([
        getTranslations('profilePage'),
        fetchSiteImage()
    ]);
    const site = res.data.allSettings?.siteImage;

    return {
        title: tr('metaTitle'),
        description: tr('metaDesc'),
        robots: { index: false, follow: false },
        openGraph: {
            title: tr('metaTitle'),
            description: tr('metaDesc'),
            images: site ? [`${process.env.NEXT_PUBLIC_API_URL}${process.env.NEXT_PUBLIC_MEDIA_URL}${site}`] : undefined,
        },
    }
}

function Stat({ label, value, colorClass = "text-slate-900" }: { label: string; value: number | string, colorClass?: string }) {
    return (
        <div className="flex flex-col items-center justify-center p-4 dark:bg-(--dark-color) w-full rounded-xl rounded-r-none">
            <Typography variant="h4" component="div" className={`font-bold ${colorClass} text-center`}>
                {value}
            </Typography>
            <Typography variant="caption" color="text.secondary" className="mt-1 uppercase tracking-wider text-center font-semibold">
                {label}
            </Typography>
        </div>
    )
}

export default async function ProfilePage({ params }: { params: Promise<{ code: `${string}-${number}` }> }) {
    const [tr, { code }] = await Promise.all([
        getTranslations('profilePage'),
        params
    ]);
    
    const { response, data: user } = await API.GET("/api/member/profile/{member_code}/", { 
        params: { path: { member_code: code } } 
    });

    if (!response.ok || !user) {
        return (
            <BodyM>
                <div className="min-h-[80svh] flex items-center justify-center p-4">
                    <Paper elevation={0} className="w-full max-w-lg border border-red-100 p-8 text-center bg-red-50/50 rounded-2xl">
                        <Typography variant="h6" color="error" fontWeight="bold">{tr('error')}</Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                            We couldn&apos;t load the profile for {code}.
                        </Typography>
                    </Paper>
                </div>
            </BodyM>
        )
    }

    return (
        <BodyM>
            <div className="min-h-screen w-full dark:bg-(--dark-color) bg-slate-50/50 py-8 px-4">
                <div className="max-w-5xl mx-auto flex flex-col gap-8">
                    
                    <Paper elevation={0} className="w-full overflow-hidden rounded-2xl border dark:border-[#3d3d3d] border-slate-200 shadow-sm">
                        <div className="h-32 bg-blue-50/80 w-full relative border-b border-slate-100"></div>
                        
                        <div className="px-6 sm:px-10 pb-8 relative">
                            <div className="flex flex-col sm:flex-row gap-6 items-start sm:items-end -mt-16 sm:-mt-12 mb-6">
                                <Avatar 
                                    sx={{ 
                                        width: 100, 
                                        height: 100, 
                                        fontSize: '3rem', 
                                        bgcolor: 'primary.main',
                                        border: '4px solid white',
                                        boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                                    }}
                                >
                                    {user.name[0].toUpperCase()}
                                </Avatar>
                                
                                <div className="flex flex-col gap-2 pb-2">
                                    <Typography variant="h4" component="h1" fontWeight="800" color="text.primary">
                                        {user.name}
                                    </Typography>
                                    <div className="flex flex-wrap gap-2">
                                        <Chip label={tr('track', { name: user.track.name })} color="primary" variant="outlined" size="small" />
                                        <Chip label={tr('code', { code: user.code || '' })} color="default" size="small" />
                                    </div>
                                </div>
                            </div>

                            <Divider sx={{ my: 3 }} />

                            <div className="grid grid-cols-3 divide-x divide-slate-100 dark:bg-transparent bg-slate-50/50 rounded-xl border border-slate-100">
                                <Stat label={tr("abs")} value={user.absents} colorClass={user.absents > 3 ? "text-red-500" : "dark:text-white text-slate-900"} />
                                <Stat label={tr("sent")} value={user.total_tasks_sent} colorClass="text-blue-600" />
                                <Stat label={tr("missing")} value={user.missing_tasks} colorClass={user.missing_tasks > 0 ? "text-amber-500" : "text-emerald-500"} />
                            </div>
                        </div>
                    </Paper>

                    <div>
                        <Typography variant="h6" fontWeight="bold" sx={{ mb: 3, px: 1 }}>
                            {tr('sent')}
                        </Typography>
                        <div className='flex flex-wrap gap-6 justify-start'>
                            <MemberTasks memberProfile={user} track={user.track.name} />
                        </div>
                    </div>
                    
                </div>
            </div>
        </BodyM>
    )
}