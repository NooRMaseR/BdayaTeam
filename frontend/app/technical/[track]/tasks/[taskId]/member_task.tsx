'use client';

import { AppBar, Dialog, DialogContent, IconButton, ListItem, ListItemText, Slide, Toolbar, Typography } from '@mui/material';
import type { components } from '@/app/generated/api_types';
import { TransitionProps } from '@mui/material/transitions';
import CloseIcon from '@mui/icons-material/Close';
import Link from 'next/link';
import React from 'react';
import SmartTaskLoader from '@/app/components/smartTaskLoader';

type MemberTaskItemProps = {
    tasksRecived: components['schemas']['RecivedTask'][];
}

type TaskShowCaseProps = {
    open: boolean;
    task: MemberTaskItemProps['tasksRecived'][0] | null;
    onClose: () => void;
}

type MembersRecivedTaskItem = {
    task: MemberTaskItemProps['tasksRecived'][0];
    onClick: (task: MemberTaskItemProps['tasksRecived'][0]) => void;
}

const Transition = React.forwardRef(function Transition(
    props: TransitionProps & {
        children: React.ReactElement<unknown>;
    },
    ref: React.Ref<unknown>,
) {
    return <Slide direction="up" ref={ref} {...props} />;
});

function TaskShowCase({ open, task, onClose }: TaskShowCaseProps) {
    return (
        <Dialog
            open={open}
            fullScreen
            slots={{
                transition: Transition,
            }}
        >
            <AppBar >
                <Toolbar>
                    <IconButton edge='start' onClick={onClose}>
                        <CloseIcon />
                    </IconButton>
                    <Typography>{task?.member.name} - {task?.member.code}</Typography>
                </Toolbar>
            </AppBar>
            <DialogContent sx={{pt: '5rem'}}>
                <Typography>Media Recived:</Typography>
                {task?.files_url.map(file => <ol key={file.id}>
                    <SmartTaskLoader task_id={file.id} />
                    {/* <Link href={`${process.env.NEXT_PUBLIC_API_URL}${url}`} download>{url}</Link> */}
                </ol>)}
                <Typography>Notes: {task?.notes}</Typography>
            </DialogContent>
        </Dialog>
    )
}

function MembersRecivedTaskItem({ task, onClick }: MembersRecivedTaskItem) {
    const handleClick = () => onClick(task);

    return (
        <ListItem key={task.id} onClick={handleClick} sx={{cursor: 'pointer'}}>
            <ListItemText>
                {task.member.name} - {task.member.code}
            </ListItemText>
        </ListItem>
    )
}

export default function MembersRecivedTasks({ tasksRecived }: MemberTaskItemProps) {
    const [selectedTask, setSelectedTask] = React.useState<TaskShowCaseProps['task'] | null>(null);
    const [open, setOpen] = React.useState<boolean>(false);

    const openDlg = (task: MembersRecivedTaskItem['task']) => {
        setSelectedTask(task);
        setOpen(true);
    };
    const closeDlg = () => setOpen(false);

    return (
        <>
            <TaskShowCase open={open} task={selectedTask} onClose={closeDlg} />
            {tasksRecived.map(task =>
                <MembersRecivedTaskItem key={task.id} task={task} onClick={openDlg} />
            )}
        </>
    )
}
