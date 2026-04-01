'use client';

import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';
import Typography from '@mui/material/Typography';
import Toolbar from '@mui/material/Toolbar';
import Divider from '@mui/material/Divider';
import Button from '@mui/material/Button';
import Avatar from '@mui/material/Avatar';
import AppBar from '@mui/material/AppBar';
import Dialog from '@mui/material/Dialog';
import Slide from '@mui/material/Slide';
import Paper from '@mui/material/Paper';

import type { TransitionProps } from '@mui/material/transitions';
import TaskShowButton from '@/app/components/task_show_button';
import type { components } from '../generated/api_types';
import LocaledTextField from './localed_textField';
import { useTranslations } from 'next-intl';
import { useForm } from 'react-hook-form';
import API from '@/app/utils/api.client';
import { toast } from 'sonner';
import React from 'react';

export type MemberTaskItemProps = {
    tasksRecived: components['schemas']['RecivedTask'][];
    track?: string;
}

export type TaskShowCaseProps = {
    open: boolean;
    editable?: boolean;
    task: MemberTaskItemProps['tasksRecived'][0] | null;
    onSuccess?: (signedId: number) => void;
    onClose: () => void;
}

type SignTask = components['schemas']['TaskSigningRequest'];

const Transition = React.forwardRef(function Transition(
    props: TransitionProps & { children: React.ReactElement<unknown> },
    ref: React.Ref<unknown>,
) {
    return <Slide direction="up" ref={ref} {...props} />;
});


export default function TaskShowCase({ open, task, onSuccess, onClose, editable = true }: TaskShowCaseProps) {
    const tr = useTranslations('taskPage');
    const { register, handleSubmit } = useForm<SignTask>();
    const onCloseRef = React.useRef(onClose);

    React.useEffect(() => {
        onCloseRef.current = onClose;
    }, [onClose]);

    React.useEffect(() => {
        if (!open) return;
        window.history.pushState({ dialogOpen: true }, '');

        const handleBackState = () => {
            onCloseRef.current();
        }

        window.addEventListener('popstate', handleBackState);
        return () => {
            window.removeEventListener('popstate', handleBackState);
            if (window.history.state?.dialogOpen === true) {
                window.history.back();
            }
        }
    }, [open]);

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
            
        >
            <AppBar className='dark:bg-(--dark-color)! bg-white p-0!' sx={{ position: 'sticky', top: 0, bgcolor: "white", color: 'text.primary', boxShadow: 'none', borderBottom: 1, borderColor: 'divider', zIndex: 10 }}>
                <Toolbar className="flex justify-between items-center dark:bg-(--dark-color)! bg-white px-4!">
                    <div className="flex items-center gap-3 min-w-0">
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
                        {task.files_url?.length ? task.files_url.map((file) => (
                            <Paper key={file.id} elevation={0} className="border border-slate-200 overflow-hidden rounded-xl bg-white p-2">
                                <TaskShowButton task_id={file.id} fileName={`File ${file.file_name || "unknown"}`} />
                            </Paper>
                        )) : (
                            <Typography color="text.secondary" className="italic">No files submitted.</Typography>
                        )}
                    </div>
                </div>

                {/* Right Side (info) */}
                <div className="w-full md:w-96 dark:bg-(--dark-color) bg-white border-t md:border-t-0 md:border-l border-slate-200 flex flex-col h-auto md:h-full shadow-none md:shadow-[-4px_0_24px_-16px_rgba(0,0,0,0.1)]">
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
                                <LocaledTextField
                                    {...register('degree', { required: true })}
                                    label={tr("degree")}
                                    type="number"
                                    inputMode="numeric"
                                    fullWidth
                                    variant="outlined"
                                    required
                                />
                                <LocaledTextField
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