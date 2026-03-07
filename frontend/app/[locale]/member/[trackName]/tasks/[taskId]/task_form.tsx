'use client';

import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';

import type { components } from '@/app/generated/api_types';
import { useForm, useWatch } from 'react-hook-form';
import { useRouter } from '@/i18n/navigation';
import { useTranslations } from 'next-intl';
import API from '@/app/utils/api.client';
import { useState } from 'react';
import { toast } from 'sonner';

type TaskActionsProps = {
    task: components['schemas']['Task'];
    track_name: string;
}

type TaskMemberSend = components['schemas']['task-member-inputRequest'];

export default function TaskForm({ task, track_name }: TaskActionsProps) {
    const [isLoading, setIsloading] = useState<boolean>(false);
    const tr = useTranslations('taskPage');
    const router = useRouter();
    
    const { register, handleSubmit, control, setValue, formState: { errors } } = useForm<TaskMemberSend>({
        defaultValues: {
            task_id: task.id
        }
    });

    const selectedFiles = useWatch({ control, name: 'file' });

    const sendTaskRequest = (data: TaskMemberSend) => {
        setIsloading(true);
        
        const promise = API.POST('/api/member/tasks/', {
            body: (() => {
                const fd = new FormData();
                fd.append('task_id', data.task_id.toString());
                if (data.notes) fd.append('notes', data.notes);

                if (data.file) {
                    Array.from(data.file).forEach(f => fd.append('file', f));
                }
                return fd as unknown as TaskMemberSend;
            })()
        });

        toast.promise(promise, {
            loading: tr('submiting'),
            success: () => {
                router.replace(`/member/${track_name}/tasks`);
                return tr('taskSub');
            },
            error: (err) => {
                if (err instanceof Error && err.message === "EXPIRED") {
                    return tr('taskSubEx');
                }
                return tr("taskSubError");
            },
            finally: () => setIsloading(false)
        });
    };

    const clearFiles = () => setValue('file', undefined);

    return (
        <Paper elevation={0} className="border border-slate-200 rounded-2xl overflow-hidden bg-white p-6 md:p-8">
            <form onSubmit={handleSubmit(sendTaskRequest)} className='flex flex-col gap-6'>
                
                <div className="w-full">
                    <Typography variant="subtitle2" fontWeight="bold" sx={{ mb: 1 }}>
                        {tr('attach')}
                    </Typography>
                    
                    {!selectedFiles || selectedFiles.length === 0 ? (
                        <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-slate-300 rounded-xl hover:bg-slate-50 hover:border-blue-500 transition-colors cursor-pointer group">
                            <div className="flex flex-col items-center justify-center pt-5 pb-6">
                                <CloudUploadIcon className="w-8 h-8 mb-2 text-slate-400 group-hover:text-blue-500 transition-colors" />
                                <Typography variant="body2" color="text.secondary">
                                    <span className="font-semibold text-blue-600">Click to upload</span>
                                </Typography>
                            </div>
                            <input 
                                type="file" 
                                className="hidden" 
                                multiple 
                                {...register('file')} 
                            />
                        </label>
                    ) : (
                        <div className="border border-slate-200 rounded-xl p-4 bg-slate-50 flex flex-col gap-2">
                            <div className="flex justify-between items-center mb-2">
                                <Typography variant="caption" fontWeight="bold" color="text.secondary" className="uppercase tracking-wider">
                                    {selectedFiles.length} File(s) Selected
                                </Typography>
                                <IconButton size="small" onClick={clearFiles} color="error">
                                    <DeleteOutlineIcon fontSize="small" />
                                </IconButton>
                            </div>
                            <div className="flex flex-col gap-2 max-h-40 overflow-y-auto">
                                {Array.from(selectedFiles).map((file, i) => (
                                    <div key={i} className="flex items-center gap-2 bg-white border border-slate-200 p-2 rounded-lg">
                                        <AttachFileIcon fontSize="small" className="text-slate-400" />
                                        <Typography variant="body2" className="truncate flex-1 font-medium">
                                            {(file as unknown as File).name}
                                        </Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            {((file as unknown as File).size / 1024 / 1024).toFixed(2)} MB
                                        </Typography>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                <div>
                    <Typography variant="subtitle2" fontWeight="bold" sx={{ mb: 1 }}>
                        {tr('notes')}
                    </Typography>
                    <TextField 
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