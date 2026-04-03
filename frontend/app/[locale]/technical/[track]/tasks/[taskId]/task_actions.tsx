'use client';

import DialogContentText from '@mui/material/DialogContentText';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';

import { type FieldErrors, useForm, UseFormHandleSubmit, UseFormRegister, Controller, type Control } from 'react-hook-form';
import { DateTimePicker, LocalizationProvider } from '@mui/x-date-pickers';
import LocaledTextField from '@/app/components/localed_textField';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import type { components } from '@/app/generated/api_types';
import { useLocale, useTranslations } from 'next-intl';
import { useRouter } from '@/i18n/navigation';
import dayjs from '@/app/utils/dayjs.client';
import API from '@/app/utils/api.client';
import { useState } from 'react';
import { toast } from 'sonner';

type TaskActionsProps = {
    task: components['schemas']['TaskResponse'];
    track_name: string;
}

type DeleteDialogProps = {
    open: boolean;
    onAccept: () => void;
    onCancel: () => void;
    taskNumber: number;
    isLoading: boolean;
}

type UpdateTaskProps = components['schemas']['TaskResponse'];

type EditDialogProps = Omit<DeleteDialogProps, 'onAccept'> & {
    onAccept: (data: UpdateTaskProps) => void;
    register: UseFormRegister<UpdateTaskProps>;
    handleSubmit: UseFormHandleSubmit<UpdateTaskProps>;
    control: Control<UpdateTaskProps>;
    errors: FieldErrors<UpdateTaskProps>;
}

function DeleteDialog({ open, onAccept, onCancel, taskNumber, isLoading }: DeleteDialogProps) {
    const tr = useTranslations('taskPage');
    return (
        <Dialog open={open} PaperProps={{ sx: { borderRadius: 2 } }}>
            <DialogTitle fontWeight="bold" color="error">{tr('deleteTask', {taskNumber})}</DialogTitle>
            <DialogContent>
                <DialogContentText className="mb-2 text-slate-700">{tr('deleteTaskDesc')}</DialogContentText>
                <DialogContentText className="text-slate-500 text-sm font-medium">{tr('deleteTaskDesc2')}</DialogContentText>
            </DialogContent>
            <DialogActions sx={{ p: 2, pt: 0 }}>
                <Button onClick={onCancel} disabled={isLoading} color="inherit">{tr('cancel')}</Button>
                <Button variant='contained' color='error' onClick={onAccept} disabled={isLoading} sx={{ px: 3, borderRadius: 2 }}>
                    {tr('delete')}
                </Button>
            </DialogActions>
        </Dialog>
    )
}

function EditDialog({ open, onAccept, onCancel, taskNumber, isLoading, register, handleSubmit, control, errors }: EditDialogProps) {
    const tr = useTranslations('taskPage');
    const locale = useLocale();

    return (
        <Dialog open={open} scroll='paper' fullWidth maxWidth="sm" slotProps={{paper: { sx: { borderRadius: 2 } }}}>
            <DialogTitle fontWeight="bold">{tr('editTask', {taskNumber})}</DialogTitle>
            <DialogContent dividers>
                <form onSubmit={handleSubmit(onAccept)} id='edit-form' className='flex flex-col gap-5 py-2'>
                    <LocaledTextField
                        label={tr('taskNum')} 
                        {...register("task_number", { required: true, valueAsNumber: true })} 
                        required 
                        fullWidth 
                        error={!!errors.task_number} 
                        helperText={errors.task_number?.message} 
                        type="number"
                    />
                    
                    <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale={locale}>
                        <Controller
                            control={control}
                            name='expires_at'
                            rules={{ required: true }}
                            render={({ field }) => (
                                <DateTimePicker
                                    label={tr('expires')}
                                    value={field.value ? dayjs(field.value) : null}
                                    ampm={true}
                                    format='DD/MM/YYYY hh:mm a'
                                    onChange={(newValue) => field.onChange(newValue ? newValue.toISOString() : null)}
                                    slotProps={{
                                        textField: {
                                            required: true,
                                            fullWidth: true,
                                            error: !!errors.expires_at,
                                            helperText: errors.expires_at?.message
                                        }
                                    }}
                                />
                            )}
                        />
                    </LocalizationProvider>
                    
                    <LocaledTextField 
                        label={tr('taskDesc')} 
                        {...register("description", { required: true })} 
                        required
                        minRows={4} 
                        multiline 
                        error={!!errors.description} 
                        helperText={errors.description?.message} 
                    />
                </form>
            </DialogContent>
            <DialogActions sx={{ p: 2 }}>
                <Button disabled={isLoading} onClick={onCancel} color="inherit">{tr('cancel')}</Button>
                <Button color='primary' variant='contained' disabled={isLoading} type='submit' form='edit-form' sx={{ px: 4, borderRadius: 2 }}>
                    {tr('edit')}
                </Button>
            </DialogActions>
        </Dialog>
    )
}

export default function TaskActions({ task, track_name }: TaskActionsProps) {
    const [openDeleteDlg, setOpenDeleteDlg] = useState<boolean>(false);
    const [openEditDlg, setOpenEditDlg] = useState<boolean>(false);
    const [DelisLoading, setDelIsloading] = useState<boolean>(false);
    const [EditisLoading, setEditIsloading] = useState<boolean>(false);
    
    const tr = useTranslations('taskPage');
    const router = useRouter();
    
    const { register, control, handleSubmit, formState: { errors } } = useForm<UpdateTaskProps>({
        defaultValues: {
            task_number: task.task_number,
            description: task.description,
            expires_at: task.expires_at
        }
    });

    const sendDeleteRequest = () => {
        setDelIsloading(true);
        
        const promise = API.DELETE('/api/technical/tasks/{task_id}/', { 
            params: { path: { task_id: task.id } } 
        }).then(({ response, error }) => {
            if (!response.ok) throw error;
            return response;
        });

        toast.promise(promise, {
            loading: tr('deleting'),
            success: () => {
                router.replace(`/technical/${track_name}/tasks`);
                return tr('deleted');
            },
            error: tr('error'),
            finally: () => setDelIsloading(false)
        });
    };

    const sendEditRequest = (data: UpdateTaskProps) => {
        setEditIsloading(true);
        
        const promise = API.PUT('/api/technical/tasks/{task_id}/', {
            params: { path: { task_id: task.id } },
            body: data
        }).then(({ response, error }) => {
            if (!response.ok) throw error;
            return response;
        });

        toast.promise(promise, {
            loading: tr('editing'),
            success: () => {
                setOpenEditDlg(false);
                router.refresh(); 
                return tr('edited');
            },
            error: tr('notEdited'),
            finally: () => setEditIsloading(false)
        });
    };

    return (
        <div className='flex flex-wrap gap-3'>
            <DeleteDialog isLoading={DelisLoading} open={openDeleteDlg} onAccept={sendDeleteRequest} onCancel={() => setOpenDeleteDlg(false)} taskNumber={task.task_number} />
            <EditDialog isLoading={EditisLoading} open={openEditDlg} onAccept={sendEditRequest} onCancel={() => setOpenEditDlg(false)} taskNumber={task.task_number} register={register} handleSubmit={handleSubmit} control={control} errors={errors} />
            
            <Button variant='outlined' color="primary" onClick={() => setOpenEditDlg(true)} sx={{ borderRadius: 2, fontWeight: 'bold' }}>
                {tr('edit')}
            </Button>
            <Button variant='outlined' color='error' onClick={() => setOpenDeleteDlg(true)} sx={{ borderRadius: 2, fontWeight: 'bold' }}>
                {tr('delete')}
            </Button>
        </div>
    )
}