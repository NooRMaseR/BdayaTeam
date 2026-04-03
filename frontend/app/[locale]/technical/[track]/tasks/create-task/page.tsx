'use client';


import { DateTimePicker, LocalizationProvider } from '@mui/x-date-pickers';
import LocaledTextField from '@/app/components/localed_textField';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import type { components } from '@/app/generated/api_types';
import GroupTitled from '@/app/components/group_titled';
import { useLocale, useTranslations } from 'next-intl';
import { useForm, Controller } from 'react-hook-form';
import dayjs from '@/app/utils/dayjs.client';
import Button from '@mui/material/Button';
import API from '@/app/utils/api.client';
import { useState } from 'react';
import { toast } from 'sonner';

type FormCreateTask = components['schemas']['TaskCreateRequest'];

export default function AddTaskPage() {
    const { register, control, handleSubmit, setError, formState: { errors } } = useForm<FormCreateTask>();
    const [isLoading, setIsloading] = useState<boolean>(false);
    const tr = useTranslations('tasksPage');
    const locale = useLocale();

    const onSubmit = async (data: FormCreateTask) => {
        setIsloading(true);
        
        const submitPromise = API.POST("/api/technical/tasks/", {
            body: data
        }).then(({ response, error }) => {
            if (!response.ok) throw error;
            return data.task_number;
        });

        toast.promise(submitPromise, {
            loading: tr('creating'),
            success: (num) => tr('taskCreated', { num }),
            error: (errorsFound: Record<string, string[]>) => {
                Object.entries(errorsFound || {}).forEach(([key, val]) => {
                    if (['task_number', 'expires_at', 'description'].includes(key)) {
                        setError(key as keyof FormCreateTask, { message: val[0] });
                    }
                });
                return tr('error');
            },
            finally: () => setIsloading(false)
        });
    };

    return (
        <div className='flex justify-center items-center min-h-[80svh] w-full p-4'>
            <GroupTitled title={tr('taskTitle')} caption={tr('createTaskDesc')}>
                <form onSubmit={handleSubmit(onSubmit)} className='flex flex-col gap-6'>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <LocaledTextField
                            label={tr('taskNum')} 
                            {...register("task_number", { required: true, valueAsNumber: true })} 
                            required 
                            fullWidth 
                            error={!!errors.task_number} 
                            helperText={errors.task_number?.message} 
                            type='number' 
                            inputMode='numeric' 
                        />

                        <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale={locale}>
                            <Controller
                                control={control}
                                name='expires_at'
                                rules={{ required: true }}
                                render={({ field }) => (
                                    <DateTimePicker
                                        label={tr('expiresAt')}
                                        value={field.value ? dayjs(field.value) : null}
                                        ampm={true}
                                        format='DD/MM/YYYY hh:mm a'
                                        onChange={(newValue) => {
                                            field.onChange(newValue ? newValue.toISOString() : null);
                                        }}
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
                    </div>

                    <LocaledTextField
                        label={tr('taskDesc')} 
                        {...register("description", { required: true })} 
                        required
                        minRows={4} 
                        multiline 
                        fullWidth
                        error={!!errors.description} 
                        helperText={errors.description?.message} 
                    />

                    {/* Submit Area */}
                    <div className="flex justify-end mt-2">
                        <Button 
                            type='submit' 
                            variant='contained' 
                            disabled={isLoading}
                            size="large"
                            sx={{ px: 5, py: 1.5, borderRadius: 2, fontWeight: 'bold' }}
                        >
                            {isLoading ? tr('creating') : tr('create')}
                        </Button>
                    </div>
                </form>
            </GroupTitled>
        </div>
    )
}