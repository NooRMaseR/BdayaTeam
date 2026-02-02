import { List, Typography } from '@mui/material';
import MembersRecivedTasks from './member_task';
import { API } from '@/app/utils/api.server';
import TaskActions from './task_actions';
import dayjs from 'dayjs';

export default async function TaskViewPage({ params }: { params: Promise<{ taskId: number, track: string }> }) {
    const { track, taskId } = await params;
    const [currentTasks, recived] = await Promise.all(
        [
            API.GET('/api/technical/tasks/{task_id}/', { params: { path: { task_id: taskId } } }),
            API.GET('/api/technical/tasks/recived/{task_id}/', { params: { path: { task_id: taskId } } })
        ]
    );

    if (!currentTasks.response.ok || !currentTasks.data) {
        return <Typography>Could Not Load Data</Typography>
    };

    return (
        <main className='mt-10'>
            <Typography component={'h3'} variant='h3' sx={{ textAlign: "center" }}><Typography component={'span'} variant='h3' sx={{ fontWeight: "bold" }}>Task</Typography> {currentTasks.data.task_number}</Typography>
            <Typography><Typography component={'span'} sx={{ fontWeight: "bold" }}>Description</Typography> {currentTasks.data.description}</Typography>
            <Typography><Typography component={'span'} sx={{ fontWeight: "bold" }}>Expired</Typography> {currentTasks.data.expired ? 'true' : 'false'}</Typography>
            <Typography><Typography component={'span'} sx={{ fontWeight: "bold" }}>Expires At</Typography> {dayjs(currentTasks.data.expires_at).format("YYYY/MM/DD hh:MM A")}</Typography>
            <TaskActions track_name={track} task={currentTasks.data} />
            <br />
            <section>
                <List>
                    {recived.data && <MembersRecivedTasks tasksRecived={recived.data} />}
                </List>
            </section>
        </main>
    )
}
