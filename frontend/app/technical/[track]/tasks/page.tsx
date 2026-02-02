import NavigationCard from '@/app/components/navigation_card';
import { API } from '@/app/utils/api.server';
import { Typography } from '@mui/material';

export default async function TasksPage() {
    const { data, response } = await API.GET('/api/technical/tasks/');

    if (!response.ok) {
        return <Typography component={'h2'} variant='h2'>Somthing Went Wrong with status { response.status }</Typography>
    }
    return (
        <main className="w-full flex gap-6 justify-center flex-wrap mt-10">
            {data?.map(task => 
                <NavigationCard
                    key={task.id}
                    url={`tasks/${task.id}`}
                    title={`Task ${task.task_number}`}
                    desc={task.description}
                />
            )}
            <NavigationCard
                url={`tasks/create-task/`}
                title="Create Task"
                desc="Add Tasks"
            />
        </main>
    )
}
