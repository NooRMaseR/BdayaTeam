import { getTranslations } from 'next-intl/server';
import Typography from '@mui/material/Typography';
import { API } from '@/app/utils/api.server';
import BodyM from '@/app/components/bodyM';
import TaskForm from './task_form';
import dayjs from 'dayjs';
// دى صفحة التاسكات بتاعت الميمبرز
// ok? ok
export default async function TaskViewPage({ params }: { params: Promise<{ taskId: number, track_name: string }> }) {
    const { track_name, taskId } = await params;
    const [tr, { data }] = await Promise.all(
        [
            getTranslations("taskPage"),
            API.GET('/api/technical/tasks/{task_id}/', { params: { path: { task_id: taskId } } })
        ]
    )

    if (!data) {
        return <Typography>{tr('error')}</Typography>
    };

    return (
        <BodyM>
            <div className='mt-10'>
                <Typography component={'h4'} variant='h4' sx={{ textAlign: "center" }}><Typography component={'span'} variant='h4' sx={{ fontWeight: "bold" }}>{tr('task')}</Typography> {data.task_number}</Typography>
                <div className="mx-6 md:mx-16 my-6 flex flex-col gap-3">
                    <Typography><Typography component={'span'} sx={{ fontWeight: "bold" }}>{tr('desc')}</Typography> {data.description}</Typography>
                    <Typography><Typography component={'span'} sx={{ fontWeight: "bold" }}>{tr('expired')}</Typography> {data.expired && tr("yes")}</Typography>
                    <Typography><Typography component={'span'} sx={{ fontWeight: "bold" }}>{tr('expires')}</Typography> {dayjs(data.expires_at).format("YYYY/MM/DD hh:MM A")}</Typography>
                </div>
                {!data.expired && <TaskForm task={data} track_name={track_name} />}
            </div>
        </BodyM>
    )
}
