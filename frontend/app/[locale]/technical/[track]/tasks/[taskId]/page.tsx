import Typography from '@mui/material/Typography';
import LinkIcon from '@mui/icons-material/Link';
import Divider from '@mui/material/Divider';
import Paper from '@mui/material/Paper';
import Chip from '@mui/material/Chip';

import TaskImageGallery from '@/app/components/task_image_gallery';
import type { LocaleOptions } from '@/app/utils/api_types_helper';
import { getTranslations } from 'next-intl/server';
import MembersRecivedTasks from './member_task';
import dayjs from '@/app/utils/dayjs.client';
import BodyM from '@/app/components/bodyM';
import API from '@/app/utils/api.server';
import TaskActions from './task_actions';
import { Link } from '@/i18n/navigation';
import type { Metadata } from 'next';

export async function generateMetadata(): Promise<Metadata> {
    const tr = await getTranslations("taskPage");
    
    return {
        title: tr("taskView")
    }
}

export default async function TaskViewPage({ params }: { params: Promise<{locale: LocaleOptions, taskId: number, track: string }> }) {
    const {locale, track, taskId } = await params;
    const [tr, currentTasks, recived] = await Promise.all([
        getTranslations('taskPage'),
        API.GET('/api/technical/tasks/{task_id}/', { params: { path: { task_id: taskId } } }),
        API.GET('/api/technical/tasks/{task_id}/recived/', { params: { path: { task_id: taskId } } })
    ]);

    if (!currentTasks.response.ok || !currentTasks.data) {
        return (
            <BodyM>
                <div className="flex justify-center items-center min-h-[50svh]">
                    <Typography color="error" variant="h6">{tr('error')}</Typography>
                </div>
            </BodyM>
        );
    };

    const task = currentTasks.data;
    const isExpired = task.expired;

    return (
        <BodyM>
            <div className="max-w-5xl mx-auto py-8 px-4 flex flex-col gap-6">
                
                <Paper elevation={0} className="border border-slate-200 rounded-2xl overflow-hidden bg-white">
                    <div className="p-6 md:p-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                        <div className="flex flex-col gap-2">
                            <div className="flex items-center gap-3">
                                <Typography variant="h4" fontWeight="800" color="text.primary">
                                    {tr('task')} {task.task_number}
                                </Typography>
                                <Chip 
                                    label={isExpired ? tr('expired') || "Expired" : "Active"} 
                                    color={isExpired ? "error" : "success"} 
                                    size="small"
                                    className="font-bold tracking-wide uppercase"
                                />
                            </div>
                            <Typography variant="body2" color="text.secondary" className="flex items-center gap-1 font-medium">
                                {tr('expires')}: {dayjs(task.expires_at).locale(locale).format("MMMM D, YYYY • h:mm A")}
                            </Typography>
                        </div>
                        
                        <TaskActions track_name={track} task={task} />
                    </div>

                    <Divider />

                    <div className="p-6 md:p-8 dark:bg-(--dark-color) bg-slate-50/50">
                        <Typography variant="overline" color="primary" fontWeight="bold">
                            {tr('desc')}
                        </Typography>
                        <Typography variant="body1" className="mt-2 whitespace-pre-wrap leading-relaxed">
                            {task.description}
                        </Typography>
                    </div>

                    {task.links && task.links.length > 0 && (
                        <div className="p-6 md:p-8 dark:bg-(--dark-color) bg-slate-50/50 border-t border-slate-200">
                            <Typography variant="overline" color="primary" fontWeight="bold">
                                {tr('urls')}
                            </Typography>
                            <div className="flex flex-col gap-3 mt-3">
                                {task.links.map((url: string, idx: number) => {
                                    return (
                                        <Link
                                            key={idx} 
                                            href={url} 
                                            target="_blank" 
                                            rel="noopener noreferrer" 
                                            className="flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 hover:underline transition-colors w-fit bg-blue-50 dark:bg-blue-900/20 px-3 py-2 rounded-lg"
                                        >
                                            <LinkIcon fontSize="small" />
                                            <Typography variant="body2" fontWeight="medium" className="truncate max-w-md">
                                                {url}
                                            </Typography>
                                        </Link>
                                    );
                                })}
                            </div>
                        </div>
                    )}
                    <TaskImageGallery images={task.images} title={tr("images")} />

                </Paper>
                
                {recived.data && <MembersRecivedTasks tasksRecived={recived.data} track={track} />}
            </div>
        </BodyM>
    )
}