'use client';

import { MembersRecivedTaskItem, TaskShowCase } from '../../technical/[track]/tasks/[taskId]/member_task';
import type { components } from '@/app/generated/api_types';
import Typography from '@mui/material/Typography';
import { useTranslations } from 'next-intl';
import { useState } from 'react';

type MemberTasksProps = {
    memberProfile: components['schemas']['MemberProfile'];
}

type Task = MemberTasksProps['memberProfile']['tasks'][0] | null;

export default function MemberTasks({ memberProfile }: MemberTasksProps) {
    const tr = useTranslations('memebersTasksPage');
    const [open, setOpen] = useState<boolean>(false);
    const [selectedTask, setSelecteTask] = useState<Task>(null);

    const onClick = (task: Task) => {
        setSelecteTask(task);
        setOpen(true);
    };

    const onClose = () => {
        setSelecteTask(null);
        setOpen(false);
    };

    if (!memberProfile?.tasks || memberProfile.tasks.length === 0) {
        return (
            <Typography color="text.secondary" className="italic w-full text-center py-8">
                No tasks available for this member yet.
            </Typography>
        );
    }


    return (
        <>
            <TaskShowCase open={open} onClose={onClose} task={selectedTask} editable={false} />
            {memberProfile.tasks.map(task =>
                <MembersRecivedTaskItem
                    key={task.id}
                    task={task}
                    showSigned
                    onClick={() => onClick(task)}
                    overrideText={{ primary: tr('task', { number: task.task.task_number }) }}
                />
            )}
        </>
    )
}