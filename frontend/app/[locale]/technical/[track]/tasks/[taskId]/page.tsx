import { getTranslations } from 'next-intl/server';
import Typography from '@mui/material/Typography';
import MembersRecivedTasks from './member_task';
import { API } from '@/app/utils/api.server';
import TaskActions from './task_actions';
import dayjs from 'dayjs';

export default async function TaskViewPage({ params }: { params: Promise<{ taskId: number, track: string }> }) {
    const { track, taskId } = await params;
    const [tr, currentTasks, recived] = await Promise.all(
        [
            getTranslations('taskPage'),
            API.GET('/api/technical/tasks/{task_id}/', { params: { path: { task_id: taskId } } }),
            API.GET('/api/technical/tasks/recived/{task_id}/', { params: { path: { task_id: taskId } } })
        ]
    );

    if (!currentTasks.response.ok || !currentTasks.data) {
        return <Typography>{tr('error')}</Typography>
    };

    return (
        <main className='mt-24'>
            <Typography component={'h4'} variant='h4' sx={{ textAlign: "center" }}><Typography component={'span'} variant='h4' sx={{ fontWeight: "bold" }}>{tr('task')}</Typography> {currentTasks.data.task_number}</Typography>
            <div className="mx-4 my-6 flex flex-col gap-2">
                <Typography sx={{ fontSize: 20 }}><Typography component={'span'} sx={{ fontWeight: "bold", fontSize: 22 }}>{tr('desc')}</Typography>: {currentTasks.data.description}</Typography>
                <Typography sx={{ fontSize: 20 }}><Typography component={'span'} sx={{ fontWeight: "bold", fontSize: 22 }}>{tr('expired')}</Typography>: {currentTasks.data.expired && tr("yes")}</Typography>
                <Typography sx={{ fontSize: 20 }}><Typography component={'span'} sx={{ fontWeight: "bold", fontSize: 22 }}>{tr('expires')}</Typography>: {dayjs(currentTasks.data.expires_at).format("YYYY/MM/DD hh:MM A")}</Typography>
            </div>
            <TaskActions track_name={track} task={currentTasks.data} />
            <br />
            <section>
                {recived.data && <MembersRecivedTasks tasksRecived={recived.data} />}
            </section>
        </main>
    )
}
