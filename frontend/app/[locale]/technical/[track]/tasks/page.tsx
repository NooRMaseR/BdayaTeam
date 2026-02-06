import NavigationCard from '@/app/components/navigation_card';
import { getTranslations } from 'next-intl/server';
import Typography from '@mui/material/Typography';
import { API } from '@/app/utils/api.server';
import BodyM from '@/app/components/bodyM';

export default async function TasksPage() {
    const [tr, { data, response }] = await Promise.all(
        [
            getTranslations("tasksPage"),
            API.GET('/api/technical/tasks/')
        ]
    );

    if (!response.ok) {
        return <Typography component={'h2'} variant='h2'>Somthing Went Wrong with status { response.status }</Typography>
    }
    return (
        <BodyM>
            <div className="flex justify-center items-center min-h-[calc(100vh-105px)] flex-wrap gap-6">
                {data?.map(task =>
                    <NavigationCard
                        key={task.id}
                        url={`tasks/${task.id}`}
                        title={tr('task', {number: task.task_number})}
                        desc={task.description}
                    />
                )}
                <NavigationCard
                    url={`tasks/create-task/`}
                    title={tr('createTask')}
                    desc={tr('createTaskDesc')}
                />
            </div>
        </BodyM>
    )
}
