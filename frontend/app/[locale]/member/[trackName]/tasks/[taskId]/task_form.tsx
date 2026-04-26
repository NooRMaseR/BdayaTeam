'use client';

import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';

import UploadMemberTaskFiles from '@/app/components/upload_member_task_files';
import type { MemberTaskSend } from '@/app/utils/api_types_helper';
import LocaledTextField from '@/app/components/localed_textField';
import type { components } from '@/app/generated/api_types';
import { useForm, useWatch } from 'react-hook-form';
import { useRouter } from '@/i18n/navigation';
import { useTranslations } from 'next-intl';
import API from '@/app/utils/api.client';
import { useState } from 'react';
import { toast } from 'sonner';

type TaskActionsProps = {
    task: components['schemas']['TaskMSGSerializer'];
    track_name: string;
    extensions: components['schemas']['TrackExtenstionsSerializer']['extensions'];
}

export default function TaskForm({ task, track_name, extensions }: TaskActionsProps) {
    const [isLoading, setIsloading] = useState<boolean>(false);
    const tr = useTranslations('taskPage');
    const router = useRouter();
    
    const { register, handleSubmit, control, setValue, formState: { errors } } = useForm<MemberTaskSend>({
        defaultValues: {
            task_id: task.id
        }
    });

    const { onChange: onRHFChange, ...resetFilesRegister } = register('files');

    const selectedFiles = useWatch({ control, name: 'files' });

    const sendTaskRequest = (data: MemberTaskSend) => {
        setIsloading(true);
        
        const promise = async () => {
            const res = await API.POST('/api/member/tasks/', {
                body: {
                    task_id: data.task_id,
                    notes: data.notes,
                    files: (data.files ? Array.from(data.files) : []) as unknown as string
                },
                bodySerializer(body) {
                    const fd = new FormData();
                    fd.append('task_id', JSON.stringify(body.task_id));
                    
                    if (body.notes)
                        fd.append('notes', JSON.stringify(body.notes));

                    if (body.files && body.files.length > 0) {
                        (body.files as unknown as string[]).forEach(f => fd.append('files', f));
                    }
                    return fd;
                }
            });

            if (res.response.ok) {
                return await Promise.resolve();
            }
            return await Promise.reject(res);
        };

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
                return tr("taskSubError")
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
                        onFileChange={onRHFChange}
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