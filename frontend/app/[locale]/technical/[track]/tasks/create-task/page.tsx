'use client';

import ImageUploadWithPreviews from '@/app/components/imageUploadWithPreview';
import { DateTimePicker, LocalizationProvider } from '@mui/x-date-pickers';
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import LocaledTextField from '@/app/components/localed_textField';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import GroupTitled from '@/app/components/group_titled';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import AddIcon from '@mui/icons-material/Add';
import Button from '@mui/material/Button';

import { useForm, Controller, useFieldArray } from 'react-hook-form'; 
import type { components } from '@/app/generated/api_types';
import { useLocale, useTranslations } from 'next-intl';
import dayjs from '@/app/utils/dayjs.client';
import BodyM from '@/app/components/bodyM';
import API from '@/app/utils/api.client';
import { useState } from 'react';
import { toast } from 'sonner';

type FormCreateTask = components['schemas']['TaskCreateRequestMSG'];

type TaskFormValues = Omit<FormCreateTask, 'links'> & {
    links: { url: string }[];
    images: File[];
};

export default function AddTaskPage() {
    const { register, control, handleSubmit, setError, formState: { errors } } = useForm<TaskFormValues>({
        defaultValues: {
            links: [],
            images: []
        }
    });
    
    const { fields: linkFields, append: appendLink, remove: removeLink } = useFieldArray({
        control,
        name: "links"
    });

    const [isLoading, setIsloading] = useState<boolean>(false);
    const tr = useTranslations('tasksPage');
    const locale = useLocale();

    const onSubmit = async (data: TaskFormValues) => {
        setIsloading(true);
        
        const submitPromise = API.POST("/api/technical/tasks/", {
            body: data as unknown as FormCreateTask,
            bodySerializer: () => {
                const fd = new FormData();
                fd.append('task_number', data.task_number.toString());
                fd.append('description', data.description);
                fd.append('expires_at', data.expires_at);
                
                if (data.links && data.links.length > 0) {
                    // const rowLinks = `[${data.links.map(link => `"${link.url}"`).join(",")}]`;
                    fd.append('links', JSON.stringify(data.links.map(link => link.url)));
                }

                if (data.images && data.images.length > 0) {
                    data.images.forEach(file => fd.append('images', file));
                }

                return fd;
            }
        }).then(({ response, error }) => {
            if (!response.ok) throw error;
            return data.task_number;
        });

        toast.promise(submitPromise, {
            loading: tr('creating'),
            success: (num) => tr('taskCreated', { num }),
            error: (errorsFound: Record<string, string>) => {
                Object.entries(errorsFound || {}).forEach(([key, val]) => {
                    if (['task_number', 'expires_at', 'description'].includes(key)) {
                        setError(key as keyof TaskFormValues, { message: val as string });
                    }
                });
                return tr('error');
            },
            finally: () => setIsloading(false)
        });
    };

    return (
        <BodyM>
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
                                            minDateTime={dayjs()}
                                            label={tr('expiresAt')}
                                            value={field.value ? dayjs(field.value) : null}
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
                        <div className="border border-slate-200 p-4 rounded-xl">
                            <Typography variant="subtitle2" fontWeight="bold" sx={{ mb: 2 }}>
                                {tr('urls')}
                            </Typography>
            
                            <div className="flex flex-col gap-3">
                                {linkFields.map((field, index) => (
                                    <div key={field.id} className="flex items-center gap-2">
                                        <TextField
                                            {...register(`links.${index}.url`)}
                                            type="url"
                                            placeholder="https://..."
                                            size="small"
                                            fullWidth
                                        />
                                        <IconButton onClick={() => removeLink(index)} color="error">
                                            <DeleteOutlinedIcon />
                                        </IconButton>
                                    </div>
                                ))}
                            </div>
            
                            <Button
                                startIcon={<AddIcon />}
                                onClick={() => appendLink({ url: '' })}
                                sx={{ mt: 2 }}
                                size="small"
                            >
                                Add Link
                            </Button>
                        </div>
                        {/* 🚨 NEW IMAGES FIELD */}
                        <div className="border border-slate-200 p-4 rounded-xl">
                            <Typography variant="subtitle2" fontWeight="bold" sx={{ mb: 2 }}>
                                Reference Images (Optional)
                            </Typography>
                            <Controller
                                control={control}
                                name="images"
                                render={({ field }) => (
                                    <ImageUploadWithPreviews
                                        images={field.value}
                                        onChange={field.onChange}
                                    />
                                )}
                            />
                        </div>
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
        </BodyM>
    )
}