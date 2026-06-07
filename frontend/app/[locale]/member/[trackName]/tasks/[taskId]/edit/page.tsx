import { getTranslations } from 'next-intl/server';
import Typography from '@mui/material/Typography';
import LinkIcon from '@mui/icons-material/Link';
import Divider from '@mui/material/Divider';
import Paper from '@mui/material/Paper';
import Chip from '@mui/material/Chip';

import dayjs, { checkLateStatus } from "@/app/utils/dayjs.client";
import type { TaskViewProps } from '../page';
import BodyM from '@/app/components/bodyM';
import API from '@/app/utils/api.server';
import { Link } from '@/i18n/navigation';
import type { Metadata } from 'next';
import dynamic from 'next/dynamic';

const DynamicTaskEditForm = dynamic(() => import("./task_edit_form"));
const DynamicTaskImageGallery = dynamic(() => import("@/app/components/task_image_gallery"));

export async function generateMetadata(): Promise<Metadata> {
    const tr = await getTranslations("taskPage");

    return {
        title: tr("editingTask")
    }
}

export default async function TaskViewEditPage({ params }: TaskViewProps) {
    const { locale, trackName, taskId } = await params;
    const [tr, { data: task }, { data: extensions }] = await Promise.all([
        getTranslations("taskPage"),
        API.GET('/api/member/edit-task/{sent_task_id}/', { params: { path: { sent_task_id: taskId } } }),
        API.GET('/api/technical/extension/')
    ]);

    if (!task) {
        return (
            <BodyM>
                <div className="flex justify-center items-center min-h-[50svh]">
                    <Typography color="error" variant="h6">{tr('error')}</Typography>
                </div>
            </BodyM>
        );
    }

    const lateStatus = checkLateStatus(task.task.expires_at, locale);
    const lateString = tr(lateStatus.status, { time: lateStatus.from });
    const allowForm = !task.task.expired || task.task.can_recive_tasks_after_expiration;
    const showImages = task.task.images && task.task.images.length > 0;

    return (
        <BodyM>
            <div className="max-w-3xl mx-auto py-8 px-4 flex flex-col gap-6 mt-8">

                <Paper elevation={0} className="border border-slate-200 rounded-2xl overflow-hidden bg-white">
                    <div className="p-6 md:p-8 bg-blue-50/30">
                        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-2">
                            <Typography variant="h4" fontWeight="800" color="text.primary">
                                {tr('task')} {task.task.task_number}
                            </Typography>
                            <Chip
                                label={task.task.expired ? tr('expired') || 'Expired' : 'Active'}
                                color={task.task.expired ? "error" : "success"}
                                className="font-bold uppercase tracking-wide"
                            />
                        </div>
                        <Typography variant="subtitle2" color="text.secondary" className="font-medium">
                            {tr('expires')}: {dayjs(task.task.expires_at).locale(locale).format("MMMM D, YYYY • h:mm A")}
                        </Typography>
                    </div>

                    <Divider />

                    <div className="p-6 md:p-8">
                        <Typography variant="overline" color="primary" fontWeight="bold">
                            {tr('desc')}
                        </Typography>
                        <Typography variant="body1" className="mt-2 whitespace-pre-wrap leading-relaxed text-slate-700">
                            {task.task.description}
                        </Typography>
                    </div>

                    {task.task.links && task.task.links.length > 0 && (
                        <div className="p-6 md:p-8 dark:bg-(--dark-color) bg-slate-50/50 border-t border-slate-200">
                            <Typography variant="overline" color="primary" fontWeight="bold">
                                {tr('urls')}
                            </Typography>
                            <div className="flex flex-col gap-3 mt-3">
                                {task.task.links.map((url, idx: number) => {
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

                    {showImages && <DynamicTaskImageGallery images={task.task.images} title={tr('images')} />}
                </Paper>

                <div className="mt-4">
                    <Typography variant="h6" fontWeight="bold" sx={{ mb: 3, px: 1 }}>
                        {tr('sub')}
                    </Typography>
                    {task.task.expired && (
                        <Paper elevation={0} className="p-6 text-center border border-red-100 bg-red-50/50 rounded-2xl">
                            <Typography color="error" fontWeight="medium">
                                {lateString}.
                            </Typography>
                        </Paper>
                    )}
                    {allowForm && <DynamicTaskEditForm task={task} track_name={trackName} extensions={extensions?.extensions} />}
                </div>
            </div>
        </BodyM>
    )
}