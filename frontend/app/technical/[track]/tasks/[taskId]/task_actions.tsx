'use client';

import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, TextField } from '@mui/material';
import { FieldErrors, useForm, UseFormHandleSubmit, UseFormRegister, UseFormSetValue } from 'react-hook-form';
import { DateTimePicker, LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import type { components } from '@/app/generated/api_types';
import { API } from '@/app/utils/api.client';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { toast } from 'sonner';

type TaskActionsProps = {
    task: components['schemas']['Task'];
    track_name: string;
}

type DeleteDialogProps = {
    readonly open: boolean;
    onAccept: () => void;
    onCancel: () => void;
    readonly taskNumber: number;
    isLoading: boolean;
}

type UpdateTaskProps = components['schemas']['updateTaskRequest'];

type EditDialogProps = Omit<DeleteDialogProps, 'onAccept'> & {
    onAccept: (data: UpdateTaskProps) => void;
    register: UseFormRegister<UpdateTaskProps>;
    handleSubmit: UseFormHandleSubmit<UpdateTaskProps>;
    setValue: UseFormSetValue<UpdateTaskProps>;
    readonly errors: FieldErrors<UpdateTaskProps>;
}

function DeleteDialog({ open, onAccept, onCancel, taskNumber, isLoading }: DeleteDialogProps) {
    return (
        <Dialog open={open}>
            <DialogTitle>Delete Task {taskNumber}?</DialogTitle>
            <DialogContent>
                <DialogContentText>Are You Sure That You Want to Delete This Task?</DialogContentText>
                <DialogContentText>This will delete all tasks sent to this task!</DialogContentText>
            </DialogContent>
            <DialogActions>
                <Button variant='contained' onClick={onCancel} loading={isLoading}>Cancel</Button>
                <Button color='error' variant='outlined' onClick={onAccept} loading={isLoading}>Delete</Button>
            </DialogActions>
        </Dialog>
    )
}

function EditDialog({ open, onAccept, onCancel, taskNumber, isLoading, register, handleSubmit, setValue, errors }: EditDialogProps) {
    return (
        <Dialog open={open} scroll='paper'>
            <DialogTitle>Edit Task {taskNumber}</DialogTitle>
            <DialogContent>
                <form onSubmit={handleSubmit(onAccept)} id='edit-form' className='flex flex-col gap-4 mt-2 mb-2'>
                    <TextField label="Task Number" {...register("task_number")} required fullWidth error={!!errors.task_number} helperText={errors.task_number?.message} />
                    <LocalizationProvider dateAdapter={AdapterDayjs}>
                        <DateTimePicker onAccept={(v) => setValue('expires_at', v?.toISOString() || new Date().toISOString())} />
                    </LocalizationProvider>
                    <TextField label="Task Decription" {...register("description")} minRows={4} multiline error={!!errors.description} helperText={errors.description?.message} />
                </form>
            </DialogContent>
            <DialogActions>
                <Button variant='contained' loading={isLoading} onClick={onCancel}>Cancel</Button>
                <Button color='success' variant='contained' loading={isLoading} type='submit' form='edit-form'>Edit</Button>
            </DialogActions>
        </Dialog>
    )
}

export default function TaskActions({ task, track_name }: TaskActionsProps) {
    const [openDeleteDlg, setOpenDeleteDlg] = useState<boolean>(false);
    const [openEditDlg, setOpenEditDlg] = useState<boolean>(false);
    const [DelisLoading, setDelIsloading] = useState<boolean>(false);
    const [EditisLoading, setEditIsloading] = useState<boolean>(false);
    const navigation = useRouter();
    const { register, handleSubmit, setValue, formState: { errors } } = useForm<UpdateTaskProps>(
        {
            defaultValues: {
                task_number: task.task_number,
                description: task.description,
            }
        }
    );

    const handleOpenDeleteDlg = () => setOpenDeleteDlg(true);
    const handleCloseDeleteDlg = () => setOpenDeleteDlg(false);

    const handleOpenEditDlg = () => setOpenEditDlg(true);
    const handleCloseEditDlg = () => setOpenEditDlg(false);

    const sendDeleteRequest = () => {
        setDelIsloading(true);
        toast.promise(async () => {
            const { response } = await API.DELETE('/api/technical/tasks/{task_id}/', { params: { path: { task_id: task.id } } });
            if (response.ok) {
                return await Promise.resolve();
            } else {
                return await Promise.reject();
            }
        },
            {
                loading: "Deleting...",
                success() {
                    navigation.replace(`/technical/${track_name}/tasks`);
                    return "Deleted Successfully";
                },
                error: "Somthing went wrong",
                finally() {
                    setDelIsloading(false);
                },
            }
        );
    };

    const sendEditRequest = (data: UpdateTaskProps) => {
        setEditIsloading(true);
        toast.promise(async () => {
            const { response } = await API.PUT('/api/technical/tasks/{task_id}/', {
                params: { path: { task_id: task.id } },
                body: data
            });
            if (response.ok) {
                return await Promise.resolve();
            } else {
                return await Promise.reject();
            }
        },
            {
                loading: "Editing...",
                success() {
                    handleCloseEditDlg();
                    navigation.replace(`/technical/${track_name}/tasks`);
                    return "Edit Successfully";
                },
                error: "Somthing went wrong",
                finally() {
                    setEditIsloading(false);
                },
            }
        );
    };


    return (
        <div className='flex gap-4'>
            <DeleteDialog isLoading={DelisLoading} open={openDeleteDlg} onAccept={sendDeleteRequest} onCancel={handleCloseDeleteDlg} taskNumber={task.task_number} />
            <EditDialog isLoading={EditisLoading} open={openEditDlg} onAccept={sendEditRequest} onCancel={handleCloseEditDlg} taskNumber={task.task_number} register={register} handleSubmit={handleSubmit} setValue={setValue} errors={errors} />
            <Button variant='contained' onClick={handleOpenEditDlg}>Edit</Button>
            <Button variant='contained' color='error' onClick={handleOpenDeleteDlg}>Delete</Button>
        </div>
    )
}
