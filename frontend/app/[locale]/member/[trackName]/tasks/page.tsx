import NavigationCard from '@/app/components/navigation_card';
import { getTranslations } from 'next-intl/server';
import Typography from '@mui/material/Typography';
import { API } from '@/app/utils/api.server';
import BodyM from '@/app/components/bodyM';

export default async function TasksPage() {
    const [tr, { data, response }] = await Promise.all(
        [
            getTranslations("memebersTasksPage"),
            API.GET('/api/member/tasks/')
        ]
    );

    if (!response.ok) {
        return <Typography component={'h3'} variant='h3'>{tr('wrong')}</Typography>
    }
    return (
        <BodyM>
            <div className="w-full flex gap-6 justify-center flex-wrap mt-10">
                {data?.map(task =>
                    <NavigationCard
                        key={task.id}
                        url={`tasks/${task.id}`}
                        title={tr('task', {number: task.task_number})}
                        desc={<div>
                            <Typography>{task.description}</Typography>
                            <Typography>{task.expired ? tr('expired') : ''}</Typography>
                        </div>}
                    />
                )}
            </div>
        </BodyM>
    )
}
