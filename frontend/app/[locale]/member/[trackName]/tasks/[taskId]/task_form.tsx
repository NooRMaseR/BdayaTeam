'use client';

import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import type { components } from '@/app/generated/api_types';
import TextField from '@mui/material/TextField';
import { useRouter } from '@/i18n/navigation';
import { API } from '@/app/utils/api.client';
import Button from '@mui/material/Button';
import { useForm } from 'react-hook-form';
import { useState } from 'react';
import { toast } from 'sonner';

type TaskActionsProps = {
    task: components['schemas']['Task'];
    track_name: string;
}

type TaskMemberSend = components['schemas']['task-member-inputRequest'];

export default function TaskForm({ task, track_name }: TaskActionsProps) {
    const [isLoading, setIsloading] = useState<boolean>(false);
    const navigation = useRouter();
    const { register, handleSubmit, formState: { errors }, } = useForm<TaskMemberSend>(
        {
            defaultValues: {
                task_id: task.id
            }
        }
    );

    const sendTaskRequest = (data: TaskMemberSend) => {
        setIsloading(true);
        toast.promise(async () => {
            const formData = new FormData();
            formData.append('task_id', data.task_id.toString());
            formData.append('notes', data.notes || '');

            if (data.file) {
                for (let i = 0; i < data.file?.length || 0; i++) {
                    formData.append('file', data.file[i]);
                }
            };

            const { response } = await API.POST('/api/member/tasks/', {
                body: formData as unknown as TaskMemberSend
            });
            
            if (response.ok) {
                return await Promise.resolve();
            } else {
                if (response.status === 406) {
                    toast.warning("This Task is Expired.");
                }
                
                return await Promise.reject();
            }
        },
            {
                loading: "Sending...",
                success() {
                    navigation.replace(`/member/${track_name}/tasks`);
                    return "Task Sent Successfully";
                },
                error: "Somthing went wrong",
                finally() {
                    setIsloading(false);
                },

            }
        );
    };

    return (
        <div className='flex gap-4 mx-6 md:mx-16 '>
            <form onSubmit={handleSubmit(sendTaskRequest)} id='edit-form' className='flex flex-col gap-2 mt-16 mb-4'>
                <div className="bg-blue-100 py-2 px-4 cursor-pointer hover:bg-blue-200 rounded-sm transition-all duration-300">
                    <input type="file" {...register('file')} multiple />
                    <KeyboardArrowDownIcon />
                </div>
                <TextField label="Task Description" {...register("notes")} minRows={4} multiline error={!!errors.notes} helperText={errors.notes?.message} />
                <Button variant='contained' type='submit' loadingPosition='start' loading={isLoading}>Send</Button>
            </form>
        </div>
    )
}
