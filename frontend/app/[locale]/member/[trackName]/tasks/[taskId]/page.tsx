import { getTranslations } from 'next-intl/server';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import Paper from '@mui/material/Paper';
import Chip from '@mui/material/Chip';

import { checkLateStatus } from "@/app/utils/dayjs.client";
import BodyM from '@/app/components/bodyM';
import API from '@/app/utils/api.server';
import TaskForm from './task_form';
import dayjs from 'dayjs';

export default async function TaskViewPage({ params }: { params: Promise<{locale: "en" | "ar", taskId: number, track_name: string }> }) {
    const { locale, track_name, taskId } = await params;
    const [tr, { data: task }] = await Promise.all([
        getTranslations("taskPage"),
        API.GET('/api/technical/tasks/{task_id}/', { params: { path: { task_id: taskId } } })
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

    const isExpired = task.expired;
    const lateStatus = checkLateStatus(task.expires_at, locale);
    const lateString = tr(lateStatus.status, {time: lateStatus.from})

    return (
        <BodyM>
            <div className="max-w-3xl mx-auto py-8 px-4 flex flex-col gap-6 mt-8">

                <Paper elevation={0} className="border border-slate-200 rounded-2xl overflow-hidden bg-white">
                    <div className="p-6 md:p-8 bg-blue-50/30">
                        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-2">
                            <Typography variant="h4" fontWeight="800" color="text.primary">
                                {tr('task')} {task.task_number}
                            </Typography>
                            <Chip
                                label={isExpired ? tr('expired') || 'Expired' : 'Active'}
                                color={isExpired ? "error" : "success"}
                                className="font-bold uppercase tracking-wide"
                            />
                        </div>
                        <Typography variant="subtitle2" color="text.secondary" className="font-medium">
                            {tr('expires')}: {dayjs(task.expires_at).locale(locale).format("MMMM D, YYYY • h:mm A")}
                        </Typography>
                    </div>

                    <Divider />

                    <div className="p-6 md:p-8">
                        <Typography variant="overline" color="primary" fontWeight="bold">
                            {tr('desc')}
                        </Typography>
                        <Typography variant="body1" className="mt-2 whitespace-pre-wrap leading-relaxed text-slate-700">
                            {task.description}
                        </Typography>
                    </div>
                </Paper>

                <div className="mt-4">
                    <Typography variant="h6" fontWeight="bold" sx={{ mb: 3, px: 1 }}>
                        {tr('sub')}
                    </Typography>
                    {isExpired && (
                        <Paper elevation={0} className="p-6 text-center border border-red-100 bg-red-50/50 rounded-2xl">
                            <Typography color="error" fontWeight="medium">
                                {lateString}.
                            </Typography>
                        </Paper>
                    )}
                    <TaskForm task={task} track_name={track_name} />
                </div>
            </div>
        </BodyM>
    )
}