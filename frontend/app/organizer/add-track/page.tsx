'use client';

import type { components } from '@/app/generated/api_types';
import FilePicker from '@/app/components/file_picker';
import { Button, TextField } from '@mui/material';
import { API } from '@/app/utils/api.client';
import { useForm } from 'react-hook-form';
import { useState } from 'react';
import { toast } from 'sonner';

type CreateTrack = components['schemas']['TrackRequest'];

export default function AddTrackPage() {
    const { register, handleSubmit, setError, setValue, formState: { errors } } = useForm<CreateTrack>();
    const [trackPreviewImage, setTrackPreviewImage] = useState<string | null>(null);
    const [trackFormImage, setTrackFormImage] = useState<File | null>(null);
    const [isLoading, setIsloading] = useState<boolean>(false);
    const validData = ["track", "description", "prefix", 'image'] as const;


    const handleImage = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            setTrackFormImage(e.target.files[0]);
            const obj = URL.createObjectURL(e.target.files[0]);
            setTrackPreviewImage(obj);
            return () => URL.revokeObjectURL(obj);
        }
    }


    const onSubmit = (data: CreateTrack) => {
        setIsloading(true);
        toast.promise(async () => {
            const formData = new FormData();
            formData.set("image", trackFormImage as Blob)
            formData.set("track", data.track)
            formData.set("description", data.description || '')
            formData.set("prefix", data.prefix)

            const { response, error } = await API.POST("/api/tracks/", {
                body: formData as unknown as {
                    track: string;
                    prefix: string;
                    description?: string | null | undefined;
                    image?: string | null | undefined;
                }
            });

            if (response.ok) {
                setValue("track", '');
                setValue("description", '');
                setValue("prefix", '');
                setTrackFormImage(null);
                setTrackPreviewImage(null);
                return await Promise.resolve(data.track);
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
                success: (track) => `Track ${track} has been created successfully.`,
                error: "Error when Creating the Track",
                finally() {
                    setIsloading(false);
                },
            }
        );
    };

    return (
        <div className='flex justify-center items-center h-[80svh] w-full'>
            <form onSubmit={handleSubmit(onSubmit)} className='flex flex-col h-max lg:w-[50%] md:w-[50%] sm:w-[90%] w-[90%] gap-4'>
                <h2 className='lg:text-4xl sm:text-3xl'>Enter Track Details</h2>
                <FilePicker accept='image/png,image/webp/,image/jpeg,image/jpg,image/ico' preview={trackPreviewImage} onChange={handleImage} />
                <TextField label="Track Name" {...register("track", { required: true })} required fullWidth error={!!errors.track} helperText={errors.track?.message} />
                <TextField label="Track Prefix" {...register("prefix", { required: true })} required fullWidth error={!!errors.prefix} helperText={errors.prefix?.message} />
                <TextField label="Track Decription" {...register("description")} minRows={4} multiline error={!!errors.description} helperText={errors.description?.message} />
                <Button type='submit' variant='contained' loadingPosition='start' loading={isLoading}>Create</Button>
            </form>
        </div>
    )
}
