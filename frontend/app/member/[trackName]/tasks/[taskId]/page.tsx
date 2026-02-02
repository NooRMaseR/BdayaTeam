import { API } from '@/app/utils/api.server';
import { Typography } from '@mui/material';
import TaskForm from './task_form';
import dayjs from 'dayjs';

export default async function TaskViewPage({ params }: { params: Promise<{ taskId: number, track_name: string }> }) {
    const { track_name, taskId } = await params;
    const { data } = await API.GET('/api/technical/tasks/{task_id}/', { params: { path: { task_id: taskId } } })

    if (!data) {
        return <Typography>Could Not Load Data</Typography>
    };

    return (
        <main className='mt-10'>
            <Typography component={'h3'} variant='h3' sx={{ textAlign: "center" }}><Typography component={'span'} variant='h3' sx={{ fontWeight: "bold" }}>Task</Typography> {data?.task_number}</Typography>
            <Typography><Typography component={'span'} sx={{ fontWeight: "bold" }}>Description</Typography> {data?.description}</Typography>
            <Typography><Typography component={'span'} sx={{ fontWeight: "bold" }}>Expired</Typography> {data?.expired ? 'true' : 'false'}</Typography>
            <Typography><Typography component={'span'} sx={{ fontWeight: "bold" }}>Expires At</Typography> {dayjs(data?.expires_at).format("YYYY/MM/DD hh:MM A")}</Typography>
            {!data.expired && <TaskForm task={data} track_name={track_name} />}
        </main>
    )
}
