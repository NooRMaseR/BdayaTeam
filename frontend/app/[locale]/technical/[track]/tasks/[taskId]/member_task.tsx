'use client';

import CheckIcon from '@mui/icons-material/CheckCircle';
import ListItemText from '@mui/material/ListItemText';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import CloseIcon from '@mui/icons-material/Close';
import TextField from '@mui/material/TextField';
import ListItem from '@mui/material/ListItem';
import Toolbar from '@mui/material/Toolbar';
import Divider from '@mui/material/Divider';
import Button from '@mui/material/Button';
import AppBar from '@mui/material/AppBar';
import Dialog from '@mui/material/Dialog';
import Avatar from '@mui/material/Avatar';
import Paper from '@mui/material/Paper';
import Slide from '@mui/material/Slide';
import List from '@mui/material/List';

import type { TransitionProps } from '@mui/material/transitions';
import TaskShowButton from '@/app/components/task_show_button';
import type { components } from '@/app/generated/api_types';
import { checkLateStatus } from "@/app/utils/dayjs.client";
import { useLocale, useTranslations } from 'next-intl';
import { useForm } from 'react-hook-form';
import API from '@/app/utils/api.client';
import { toast } from 'sonner';
import React from 'react';

type MemberTaskItemProps = {
    tasksRecived: components['schemas']['RecivedTask'][];
}

type TaskShowCaseProps = {
    open: boolean;
    editable?: boolean;
    task: MemberTaskItemProps['tasksRecived'][0] | null;
    onSuccess?: (signedId: number) => void;
    onClose: () => void;
}

type MembersRecivedTaskItemProps = {
    task: MemberTaskItemProps['tasksRecived'][0];
    onClick: (task: MemberTaskItemProps['tasksRecived'][0]) => void;
    showSigned?: boolean;
    overrideText?: { primary?: React.ReactNode, secondary?: React.ReactNode }
}

type SignTask = components['schemas']['TaskSigningRequest'];

const Transition = React.forwardRef(function Transition(
    props: TransitionProps & { children: React.ReactElement<unknown> },
    ref: React.Ref<unknown>,
) {
    return <Slide direction="up" ref={ref} {...props} />;
});

export function TaskShowCase({ open, task, onSuccess, onClose, editable = true }: TaskShowCaseProps) {
    const tr = useTranslations('taskPage');
    const { register, handleSubmit } = useForm<SignTask>();
    const onCloseRef = React.useRef(onClose);

    React.useEffect(() => {
        onCloseRef.current = onClose;
    }, [onClose]);

    React.useEffect(() => {
        if (!open) return;

        window.history.pushState({ dialogOpen: true }, '');

        const handlePopState = () => {
            onCloseRef.current();
        };

        window.addEventListener('popstate', handlePopState);
        return () => {
            window.removeEventListener('popstate', handlePopState);
            if (window.history.state.dialogOpen) window.history.back();
        }
    }, [open])

    const handleForm = async (dataToSend: SignTask) => {
        if (!task) {
            toast.warning("No Task Selected");
            return;
        };

        const submissionPromise = API.POST("/api/technical/tasks/recived/{task_id}/", {
            params: { path: { task_id: task.id } },
            body: dataToSend
        }).then(({ response, error }) => {
            if (!response.ok) throw error;
            return response;
        });

        toast.promise(submissionPromise, {
            loading: tr('signing'),
            success: () => {
                if (onSuccess) onSuccess(task.id);
                return tr('signed');
            },
            error: tr('error')
        });
    }

    if (!task) return null;

    return (
        <Dialog
            open={open}
            fullScreen
            slots={{ transition: Transition }}
            sx={{ bgcolor: '#f8fafc' }}
        >
            <AppBar sx={{ position: 'sticky', top: 0, bgcolor: 'white', color: 'text.primary', boxShadow: 'none', borderBottom: 1, borderColor: 'divider', zIndex: 10 }}>
                <Toolbar className="flex justify-between items-center px-4">
                    <div className="flex items-center gap-3 min-w-0 pr-4">
                        <Avatar sx={{ bgcolor: 'primary.main', width: 36, height: 36, flexShrink: 0 }}>
                            {task.member.name[0].toUpperCase()}
                        </Avatar>
                        <div className="min-w-0">
                            <Typography variant="subtitle1" fontWeight="bold" className="leading-tight truncate">
                                {task.member.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary" className="truncate block">
                                {task.member.code}
                            </Typography>
                        </div>
                    </div>
                    <IconButton edge="end" onClick={onClose} aria-label="close" sx={{ color: 'text.secondary', flexShrink: 0 }}>
                        <CloseIcon />
                    </IconButton>
                </Toolbar>
            </AppBar>

            <div className="flex flex-col md:flex-row h-full md:h-[calc(100vh-64px)] overflow-y-auto md:overflow-hidden">

                {/* Left Side (Media) */}
                <div className="flex-1 p-4 sm:p-8 md:overflow-y-auto">
                    <Typography variant="h6" fontWeight="bold" sx={{ mb: 3 }} color="text.secondary">
                        {tr('media')} ({task.files_url?.length || 0})
                    </Typography>

                    <div className="flex flex-col gap-4 sm:gap-6">
                        {task.files_url?.length ? task.files_url.map((file, index) => (
                            <Paper key={file.id} elevation={0} className="border border-slate-200 overflow-hidden rounded-xl bg-white p-2">
                                <TaskShowButton task_id={file.id} fileName={`File ${index + 1}`} />
                            </Paper>
                        )) : (
                            <Typography color="text.secondary" className="italic">No files submitted.</Typography>
                        )}
                    </div>
                </div>

                {/* Right Side (info) */}
                <div className="w-full md:w-96 bg-white border-t md:border-t-0 md:border-l border-slate-200 flex flex-col h-auto md:h-full shadow-none md:shadow-[-4px_0_24px_-16px_rgba(0,0,0,0.1)]">
                    <div className="p-6 flex-1 md:overflow-y-auto">

                        <Typography variant="overline" color="primary" fontWeight="bold">
                            {tr('notes')}
                        </Typography>
                        <Paper elevation={0} className="bg-slate-50 border border-slate-100 p-4 mt-2 mb-8 rounded-lg min-h-25">
                            <Typography variant="body2" color={task.notes ? "text.primary" : "text.secondary"} className={!task.notes ? "italic" : ""}>
                                {task.notes}
                            </Typography>
                        </Paper>

                        <Typography variant="overline" color="primary" fontWeight="bold">
                            {tr('techNotes')}
                        </Typography>
                        <Paper elevation={0} className="bg-slate-50 border border-slate-100 p-4 mt-2 mb-8 rounded-lg min-h-25">
                            <Typography variant="body2" color={task.technical_notes ? "text.primary" : "text.secondary"} className={!task.technical_notes ? "italic" : ""}>
                                {task.technical_notes}
                            </Typography>
                        </Paper>

                        {editable && (
                            <form onSubmit={handleSubmit(handleForm)} className="flex flex-col gap-5 mb-8 md:mb-0">
                                <Typography variant="h6" fontWeight="bold" sx={{ mb: -1 }}>
                                    {tr('eval')}
                                </Typography>
                                <Divider />
                                <TextField
                                    {...register('degree', { required: true })}
                                    label={tr("degree")}
                                    type="number"
                                    inputMode="numeric"
                                    fullWidth
                                    variant="outlined"
                                    required
                                />
                                <TextField
                                    {...register('technical_notes')}
                                    label={tr("memMessage")}
                                    fullWidth
                                    variant="outlined"
                                    minRows={3}
                                />
                                <Button
                                    variant="contained"
                                    type="submit"
                                    size="large"
                                    sx={{ py: 1.5, borderRadius: 2, fontWeight: 'bold' }}
                                >
                                    {tr('sign')}
                                </Button>
                            </form>
                        ) }
                    </div>
                </div>

            </div>
        </Dialog>
    )
}

export function MembersRecivedTaskItem({ task, onClick, showSigned = false, overrideText = {} }: MembersRecivedTaskItemProps) {
    const tr = useTranslations('taskPage');
    const locale = useLocale();
    const late = checkLateStatus(task.task.expires_at, locale, task.recived_at, true);
    const lateString = tr('late', { time: late.from });

    return (
        <ListItem
            onClick={() => onClick(task)}
            className="hover:bg-slate-50 transition-colors border-b border-slate-100 last:border-0 cursor-pointer"
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