import { getTranslations } from 'next-intl/server';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import Paper from '@mui/material/Paper';
import Chip from '@mui/material/Chip';

import MembersRecivedTasks from './member_task';
import BodyM from '@/app/components/bodyM';
import API from '@/app/utils/api.server';
import TaskActions from './task_actions';
import dayjs from 'dayjs';

export default async function TaskViewPage({ params }: { params: Promise<{locale: "en" | 'ar', taskId: number, track: string }> }) {
    const {locale, track, taskId } = await params;
    const [tr, currentTasks, recived] = await Promise.all([
        getTranslations('taskPage'),
        API.GET('/api/technical/tasks/{task_id}/', { params: { path: { task_id: taskId } } }),
        API.GET('/api/technical/tasks/recived/{task_id}/', { params: { path: { task_id: taskId } } })
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

                    <div className="p-6 md:p-8 bg-slate-50/50">
                        <Typography variant="overline" color="primary" fontWeight="bold">
                            {tr('desc')}
                        </Typography>
                        <Typography variant="body1" className="mt-2 whitespace-pre-wrap leading-relaxed">
                            {task.description}
                        </Typography>
                    </div>
                </Paper>
                
                {recived.data && <MembersRecivedTasks tasksRecived={recived.data} />}
            </div>
        </BodyM>
    )
}