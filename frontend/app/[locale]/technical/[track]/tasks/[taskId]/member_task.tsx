'use client';

import DialogContent from '@mui/material/DialogContent';
import ListItemText from '@mui/material/ListItemText';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import CloseIcon from '@mui/icons-material/Close';
import TextField from '@mui/material/TextField';
import ListItem from '@mui/material/ListItem';
import Toolbar from '@mui/material/Toolbar';
import Button from '@mui/material/Button';
import AppBar from '@mui/material/AppBar';
import Dialog from '@mui/material/Dialog';
import Slide from '@mui/material/Slide';
import List from '@mui/material/List';

import type { TransitionProps } from '@mui/material/transitions';
import SmartTaskLoader from '@/app/components/smartTaskLoader';
import type { components } from '@/app/generated/api_types';
import { API } from '@/app/utils/api.client';
import { useTranslations } from 'next-intl';
import { useForm } from 'react-hook-form';
import { toast } from 'sonner';
import React from 'react';

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

type SignTask = components['schemas']['TaskSigningRequest'];

const Transition = React.forwardRef(function Transition(
    props: TransitionProps & {
        children: React.ReactElement<unknown>;
    },
    ref: React.Ref<unknown>,
) {
    return <Slide direction="up" ref={ref} {...props} />;
});

function TaskShowCase({ open, task, onClose }: TaskShowCaseProps) {
    const tr = useTranslations('taskPage');
    const { register, handleSubmit } = useForm<SignTask>();
    
    const handelForm = (dataToSend: SignTask) => {
        if (task) {
            toast.promise(async () => {
                const { response } = await API.POST("/api/technical/tasks/recived/{task_id}/", {
                    params: { path: { task_id: task.id } },
                    body: dataToSend
                });

                if (response.ok) {
                    return await Promise.resolve();
                }
                return await Promise.reject();
            },
                {
                    loading: tr('signing'),
                    success() {
                        onClose();
                        return tr('signed');
                    },
                    error: tr('signed')
                }
            )
        }
    }

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
                        <CloseIcon sx={{color: 'white'}} />
                    </IconButton>
                    <Typography>{task?.member.name} - {task?.member.code}</Typography>
                </Toolbar>
            </AppBar>
            <DialogContent sx={{pt: '5rem'}}>
                <Typography>{tr('media')}</Typography>
                <List>
                    {task?.files_url.map(file => <ListItem key={file.id} className='m-4'>
                        <SmartTaskLoader task_id={file.id} />
                    </ListItem>)}
                </List>
                <Typography>{tr('notes')}: {task?.notes}</Typography>
                <form onSubmit={handleSubmit(handelForm)} className="flex flex-col gap-5 mt-10 w-50">
                    <TextField
                        {...register('degree', {required: true})}
                        label={tr("degree")}
                        type='number'
                        inputMode='numeric'
                    />
                    <Button variant='contained' type='submit'>{tr('sign')}</Button>
                </form>
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
        <div className="bg-blue-200 hover:bg-blue-300 transition-all duration-300 mx-4 my-2 rounded-md">
            <TaskShowCase open={open} task={selectedTask} onClose={closeDlg} />
            <List>
                {tasksRecived.map(task =>
                    <MembersRecivedTaskItem key={task.id} task={task} onClick={openDlg} />
                )}
            </List>
        </div>
    )
}
