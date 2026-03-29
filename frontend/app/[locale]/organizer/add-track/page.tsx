'use client';


import LocaledTextField from '@/app/components/localed_textField';
import type { components } from '@/app/generated/api_types';
import { revalidateTracks } from '@/app/utils/api_utils';
import GroupTitled from '@/app/components/group_titled';
import FilePicker from '@/app/components/file_picker';
import { useTranslations } from 'next-intl';
import BodyM from '@/app/components/bodyM';
import { useForm } from 'react-hook-form';
import Button from '@mui/material/Button';
import API from '@/app/utils/api.client';
import { useState } from 'react';
import { toast } from 'sonner';

type CreateTrack = components['schemas']['TrackRequest'];

export default function AddTrackPage() {
    const { register, handleSubmit, setError, setValue, formState: { errors } } = useForm<CreateTrack>();
    const [trackPreviewImage, setTrackPreviewImage] = useState<string | null>(null);
    const [trackFormImage, setTrackFormImage] = useState<File | null>(null);
    const [isLoading, setIsloading] = useState<boolean>(false);
    const validData = ["name", "en_description", "ar_description", "prefix", 'image'] as const;
    const tr = useTranslations('createTrackPage');


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
            formData.set("name", data.name)
            formData.set("en_description", data.en_description)
            formData.set("ar_description", data.ar_description)
            formData.set("prefix", data.prefix)

            const { response, error } = await API.POST("/api/tracks/", {
                body: formData as unknown as {
                    name: string;
                    prefix: string;
                    en_description: string;
                    ar_description: string;
                    image: string;
                }
            });

            if (response.ok) {
                setValue("name", '');
                setValue("en_description", '');
                setValue("ar_description", '');
                setValue("prefix", '');
                setTrackFormImage(null);
                setTrackPreviewImage(null);
                return await Promise.resolve(data.name);
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
                loading: tr('creating'),
                success: (track) => tr('success', {track}),
                error: tr('error'),
                finally() {
                    revalidateTracks();
                    setIsloading(false);
                },
            }
        );
    };

    return (
        <BodyM>
            <div className='flex justify-center items-center min-h-[80svh] w-full p-4'>
                <GroupTitled title={tr('enterDetails')} caption={tr('enterDesc')}>
                    <form onSubmit={handleSubmit(onSubmit)} className='flex flex-col gap-6'>
                        <div className="flex justify-center w-full mb-2">
                             <div className="w-full max-w-sm">
                                 <FilePicker accept='image/png,image/webp,image/jpeg,image/jpg,image/ico' preview={trackPreviewImage} onChange={handleImage} required />
                             </div>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                            <div className="md:col-span-3">
                                <LocaledTextField label={tr('name')} {...register("name", { required: true })} required fullWidth error={!!errors.name} helperText={errors.name?.message} />
                            </div>
                            <div className="md:col-span-1">
                                <LocaledTextField label={tr('pre')} {...register("prefix", { required: true, maxLength: {value: 2, message: tr("err_max_pre")} })} required fullWidth error={!!errors.prefix} helperText={errors.prefix?.message} />
                            </div>
                        </div>
                        <LocaledTextField label={tr('en_desc')} {...register("en_description", { required: true })} required minRows={3} multiline fullWidth error={!!errors.en_description} helperText={errors.en_description?.message} />
                        <LocaledTextField label={tr('ar_desc')} {...register("ar_description", { required: true })} required minRows={3} multiline fullWidth error={!!errors.ar_description} helperText={errors.ar_description?.message} />
 
                        <div className="flex justify-end mt-4">
                            <Button
                                type='submit'
                                variant='contained'
                                size="large"
                                disabled={isLoading}
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
