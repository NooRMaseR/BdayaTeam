'use client';

import type { CreateTrack, Track } from '@/app/utils/api_types_helper';
import { Button, TextField } from '@mui/material';
import { API } from '@/app/utils/api.client';
import { useForm } from 'react-hook-form';
import { toast } from 'sonner';

export default function AddTrackPage() {
    const { register, handleSubmit, reset, setError, formState: { errors } } = useForm<CreateTrack>();
    const validData = ["track", "description", "prefix"] as const;
    const onSubmit = async (data: CreateTrack) => {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        toast.promise<Track | any>(async () => {
            const {response, error, data: body} = await API.POST("/tracks/", {body: data});
            
            if (response.ok) {
                reset();
                return await Promise.resolve(body);
            } else {
                Object.entries(error || {}).forEach(e => {
                    const key = e[0] as keyof CreateTrack;
                    const value = (e[1] as string[])[0];

                    if (validData.includes(key)) {
                        setError(key, { message: value });
                    } else {
                        toast.error(key, { description: value, descriptionClassName: "text-gray-600!" });
                    }
                });
                return await Promise.reject(error);
            }
        },
            {
                loading: "Creating...",
                success: (data) => `Track ${data?.track} has been created successfully.`,
                error: "Error when Creating the Track",
            }
        );
    };

    return (
        <div className='flex justify-center items-center h-[80svh] w-full'>
            <form onSubmit={handleSubmit(onSubmit)} className='flex flex-col h-max lg:w-[50%] md:w-[50%] sm:w-[90%] w-[90%] gap-4'>
                <h2 className='lg:text-4xl sm:text-3xl'>Enter Track Details</h2>
                <TextField label="Track Name" {...register("track", { required: true })} required fullWidth error={!!errors.track} helperText={errors.track?.message} />
                <TextField label="Track Prefix" {...register("prefix", { required: true })} required fullWidth error={!!errors.prefix} helperText={errors.prefix?.message} />
                <TextField label="Track Decription" {...register("description")} minRows={4} multiline error={!!errors.description} helperText={errors.description?.message} />
                <Button type='submit' variant='contained'>Create</Button>
            </form>
        </div>
    )
}
