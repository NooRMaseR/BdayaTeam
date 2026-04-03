'use client';

import { MembersRecivedTaskItem } from '../../technical/[track]/tasks/[taskId]/member_task';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import type { components } from '@/app/generated/api_types';
import TaskShowCase from '@/app/components/task_show_case';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import { useAuthStore } from '@/app/utils/store';
import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/navigation';
import { useState } from 'react';

type MemberTasksProps = {
    memberProfile: components['schemas']['MemberProfileResponse'];
    track: string;
}

type Task = MemberTasksProps['memberProfile']['tasks'][0] | null;

export default function MemberTasks({ memberProfile, track }: MemberTasksProps) {
    const tr = useTranslations('memebersTasksPage');
    const userRole = useAuthStore(state => state.user?.role);
    const isMember = userRole === "member";
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
                    overrideText={{ primary: tr('task', { number: task.task.task_number }), secondary: isMember ? <Link href={`/member/${track}/tasks/${task.id}/edit`}><IconButton><EditOutlinedIcon /></IconButton></Link> : undefined }}
                />
            )}
        </>
    )
}