'use client';

import { DateTimePicker, LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import type { components } from '@/app/generated/api_types';
import { Button, TextField } from '@mui/material';
import { API } from '@/app/utils/api.client';
import { useForm } from 'react-hook-form';
import { useState } from 'react';
import { toast } from 'sonner';

type FormCreateTask = Pick<components['schemas']['TaskRequest'], 'description' | 'task_number'>;

export default function AddTaskPage() {
    const { register, handleSubmit, setError, formState: { errors } } = useForm<FormCreateTask>();
    const [isLoading, setIsloading] = useState<boolean>(false);
    const [date, setDate] = useState<string>('');

    const onSubmit = async (data: FormCreateTask) => {
        setIsloading(true);
        const dataToSend: components['schemas']['TaskRequest'] = {
            ...data,
            expires_at: date,
        }
        toast.promise(async () => {

            const { response, error } = await API.POST("/api/technical/tasks/", {
                body: dataToSend
            });

            if (response.ok) {
                return await Promise.resolve(data.task_number);
            } 
            return await Promise.reject(error);
        },
            {
                loading: "Creating...",
                success: (track) => `Task ${track} has been created successfully.`,
                error(errorsFound) {
                    Object.entries(errorsFound).forEach(v => {
                        if (['task_number', 'expires_at'].includes(v[0])) {
                            setError(v[0] as keyof FormCreateTask, { message: (v[1] as string[])[0] });
                        }
                    });
                    return "Error when Creating the Task";
                },
                finally() {
                    setIsloading(false);
                },
            }
        );
    };

    return (
        <div className='flex justify-center items-center h-[80svh] w-full'>
            <form onSubmit={handleSubmit(onSubmit)} className='flex flex-col h-max lg:w-[50%] md:w-[50%] sm:w-[90%] w-[90%] gap-4'>
                <h2 className='lg:text-4xl sm:text-3xl'>Enter Task Details</h2>
                <TextField label="Task Number" {...register("task_number", { required: true })} required fullWidth error={!!errors.task_number} helperText={errors.task_number?.message} />
                <LocalizationProvider dateAdapter={AdapterDayjs}>
                    <DateTimePicker slotProps={{ textField: {required: true} }} onAccept={(v) => setDate(v?.toISOString() || new Date().toISOString())} />
                </LocalizationProvider>
                <TextField label="Task Decription" {...register("description")} minRows={4} multiline error={!!errors.description} helperText={errors.description?.message} />
                <Button type='submit' variant='contained' loadingPosition='start' loading={isLoading}>Create</Button>
            </form>
        </div>
    )
}
