'use client';

import CheckIcon from '@mui/icons-material/CheckCircle';
import ListItemText from '@mui/material/ListItemText';
import Typography from '@mui/material/Typography';
import ListItem from '@mui/material/ListItem';
import Avatar from '@mui/material/Avatar';
import Paper from '@mui/material/Paper';
import List from '@mui/material/List';

import type { MemberTaskItemProps, TaskShowCaseProps } from '@/app/components/task_show_case';
import TaskShowCase from '@/app/components/task_show_case';
import { checkLateStatus } from "@/app/utils/dayjs.client";
import { useLocale, useTranslations } from 'next-intl';
import React from 'react';

type MembersRecivedTaskItemProps = {
    task: MemberTaskItemProps['tasksRecived'][0];
    onClick: (task: MemberTaskItemProps['tasksRecived'][0]) => void;
    showSigned?: boolean;
    overrideText?: { primary?: React.ReactNode, secondary?: React.ReactNode }
}

export function MembersRecivedTaskItem({ task, onClick, showSigned = false, overrideText = {} }: MembersRecivedTaskItemProps) {
    const tr = useTranslations('taskPage');
    const locale = useLocale();
    const late = checkLateStatus(task.task.expires_at, locale, task.recived_at, true);
    const lateString = tr('late', { time: late.from });

    return (
        <ListItem
            onClick={() => onClick(task)}
            className="dark:hover:bg-[#373737] hover:bg-gray-300 transition-colors border-b border-slate-100 last:border-0 cursor-pointer rounded-2xl"
            secondaryAction={
                late.status === "late" && <Typography color='error'>{lateString}</Typography>
            }
        >
            <div className="flex items-center gap-4 w-full py-2">
                {showSigned && task.signed && (
                    <CheckIcon fontSize="medium" sx={{color: "green"}} />
                )}
                <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.light', fontSize: '1rem' }}>
                    {task.member.name[0].toUpperCase()}
                </Avatar>
                <ListItemText
                    primary={overrideText?.primary ?? task.member.name}
                    secondary={overrideText?.secondary ?? task.member.code}
                    slotProps={{ primary: { fontWeight: 'medium' } }}
                />
            </div>
        </ListItem>
    )
}

export default function MembersRecivedTasks({ tasksRecived }: MemberTaskItemProps) {
    const [selectedTask, setSelectedTask] = React.useState<TaskShowCaseProps['task'] | null>(null);
    const [tasks, setTasks] = React.useState<MemberTaskItemProps['tasksRecived']>(tasksRecived);
    const [open, setOpen] = React.useState<boolean>(false);
    const tr = useTranslations('taskPage');

    const openDlg = (task: MembersRecivedTaskItemProps['task']) => {
        setSelectedTask(task);
        setOpen(true);
    };

    const closeDlg = () => {
        setSelectedTask(null);
        setOpen(false);
    };

    const onSign = (signedId: number) => {
        setTasks(t => t.filter((task) => task.id !== signedId));
        closeDlg();
    };

    return (
        <div>
            <Typography variant="h6" fontWeight="bold" sx={{ mb: 2, px: 1 }}>
                {tr('submited')} ({tasks.length})
            </Typography>
            <Paper elevation={0} className="border border-slate-200 rounded-xl overflow-hidden bg-white mx-4 my-2">
                <TaskShowCase open={open} task={selectedTask} onSuccess={onSign} onClose={closeDlg} />
                {tasksRecived.length > 0 && (
                    <List disablePadding>
                        {tasks.map(task =>
                            <MembersRecivedTaskItem key={task.id} task={task} onClick={openDlg} />
                        )}
                    </List>
                )}
            </Paper>
        </div>
    )
}