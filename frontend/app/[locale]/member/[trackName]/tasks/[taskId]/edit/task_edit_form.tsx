'use client';

import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';

import UploadMemberTaskFiles from '@/app/components/upload_member_task_files';
import LocaledTextField from '@/app/components/localed_textField';
import type { components } from '@/app/generated/api_types';
import { useForm, useWatch } from 'react-hook-form';
import { useRouter } from '@/i18n/navigation';
import { useTranslations } from 'next-intl';
import API from '@/app/utils/api.client';
import { useState } from 'react';
import { toast } from 'sonner';

type TaskActionsProps = {
    task: components['schemas']['RecivedTaskMSGSerializer'];
    track_name: string;
    extensions: components['schemas']['TrackExtenstionsSerializer']['extensions']
}

type TaskMemberSend = components['schemas']['RecivedTaskMSGSerializer'] & { files?: string[] };

export default function TaskEditForm({ task, track_name, extensions }: TaskActionsProps) {
    const [isLoading, setIsloading] = useState<boolean>(false);
    const tr = useTranslations('taskPage');
    const router = useRouter();

    const { register, handleSubmit, control, setValue, formState: { errors } } = useForm<TaskMemberSend>({
        defaultValues: {
            notes: task.notes || undefined
        }
    });

    const { ...resetFilesRegister } = register('files');

    const selectedFiles = useWatch({ control, name: 'files' });

    const appendFiles = (e: React.ChangeEvent<HTMLInputElement>) => {
        const newFiles = e.target.files;
        if (!newFiles || newFiles.length === 0) return;

        const dt = new DataTransfer();

        if (selectedFiles) {
            Array.from(selectedFiles).forEach(f => dt.items.add(f as unknown as File));
        }

        Array.from(newFiles).forEach(f => dt.items.add(f));

        setValue('files', dt.files as unknown as string[], { shouldValidate: true });

        e.target.value = '';
    };

    const removeFile = (indexToRemove: number) => {
        if (!selectedFiles) return;

        const dt = new DataTransfer();
        Array.from(selectedFiles).forEach((f, i) => {
            if (i !== indexToRemove) dt.items.add(f as unknown as File);
        });

        if (dt.files.length === 0) {
            setValue('files', undefined, { shouldValidate: true });
        } else {
            setValue('files', dt.files as unknown as string[], { shouldValidate: true });
        }
    };

    const sendTaskRequest = (data: TaskMemberSend) => {
        setIsloading(true);

        const promise = API.PUT('/api/member/edit-task/{sent_task_id}/', {
            params: { path: { sent_task_id: task.id } },
            body: {
                notes: data.notes ?? '',
                files: data.files ? Array.from(data.files) : []
            },
            bodySerializer(body) {
                if (body) {
                    const fd = new FormData();
                    if (body.notes) fd.append('notes', body.notes);
    
                    if (body.files && body.files.length > 0) {
                        (body.files as unknown as string[]).forEach(f => fd.append('files', f));
                    }

                    return fd;
                }
            }
        });

        toast.promise(promise, {
            loading: tr('submiting'),
            success() {
                router.replace(`/member/${track_name}/tasks`);
                return tr('taskSub');
            },
            error(error) {
                if (error.response.status === 415) {
                    return error.error.detail;
                }
                return tr("taskSubError");
            },
            finally: () => setIsloading(false)
        });
    };

    const clearFiles = () => setValue('files', undefined);

    return (
        <Paper elevation={0} className="border border-slate-200 rounded-2xl overflow-hidden bg-white p-6 md:p-8">
            <form onSubmit={handleSubmit(sendTaskRequest)} className='flex flex-col gap-6'>

                <div className="w-full">
                    <Typography variant="subtitle2" fontWeight="bold" sx={{ mb: 1 }}>
                        {tr('attach')}
                    </Typography>

                    <UploadMemberTaskFiles
                        selectedFiles={selectedFiles}
                        extensions={extensions}
                        onClear={clearFiles}
                        onRemoveFile={removeFile}
                        onFileChange={appendFiles}
                        {...resetFilesRegister}
                    />
                </div>

                <div>
                    <Typography variant="subtitle2" fontWeight="bold" sx={{ mb: 1 }}>
                        {tr('notes')}
                    </Typography>
                    <LocaledTextField
                        placeholder={tr('notes')}
                        {...register("notes")}
                        minRows={4}
                        multiline
                        fullWidth
                        error={!!errors.notes}
                        helperText={errors.notes?.message}
                    />
                </div>

                <Button
                    variant='contained'
                    type='submit'
                    size="large"
                    disabled={isLoading}
                    sx={{ py: 1.5, borderRadius: 2, fontWeight: 'bold', mt: 2 }}
                >
                    {isLoading ? tr('submiting') : tr('submitTask')}
                </Button>
            </form>
        </Paper>
    )
}