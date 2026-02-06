'use client';

import LocationSearchingOutlinedIcon from '@mui/icons-material/LocationSearchingOutlined';
import PersonOutlineOutlinedIcon from '@mui/icons-material/PersonOutlineOutlined';
import AssignmentIndOutlinedIcon from '@mui/icons-material/AssignmentIndOutlined';
import PhoneOutlinedIcon from '@mui/icons-material/PhoneOutlined';
import EmailOutlinedIcon from '@mui/icons-material/EmailOutlined';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import TextField  from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';

import { useAppDispatch, useAppSelector } from '../../utils/hooks';
import type { components } from '../../generated/api_types';
import { setCredentials } from '../../utils/states';
import { Link, useRouter } from '@/i18n/navigation';
import { API } from '../../utils/api.client';
import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import styles from "./register.module.css";
import { useForm } from 'react-hook-form';
import { toast } from 'sonner';
import Image from 'next/image';

type RegisterFormProps = {
  tracks: components['schemas']['Track'][];
  canRegister?: boolean | null
}

type SendRegister = components['schemas']['RegisterMemberRequest'];

export default function RegisterForm({ tracks, canRegister = false }: RegisterFormProps) {
  const { handleSubmit, register, setError, formState: { errors } } = useForm<SendRegister>();
  const siteImage = useAppSelector(state => state.settings.site_image);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const tr = useTranslations('registerPage');
  const dispatch = useAppDispatch();
  const router = useRouter();

  const onSubmit = async (data: SendRegister) => {
    setIsLoading(true);
    const submitRegister = async () => {
      const { data: body, error, response } = await API.POST(
        "/api/register/",
        {
          body: data
        }
      );

      if (response.ok && body) {
        dispatch(setCredentials({ isLoading: false, isAuthed: true, user: { username: body.name, role: "member", track: body.track } }));
        router.replace(`/member/${body.track?.track}`);
        return await Promise.resolve(body);
      } else {
        if (error && error instanceof Object) {
          if (!(error as Record<string, string[]>).details) {
            Object.entries(error).forEach(er => {
              setError(er[0] as keyof SendRegister, { message: (er[1] as string[])[0] });
            });
          }
        }
        return await Promise.reject();
      };
    };

    toast.promise(submitRegister(), {
      loading: tr('loading'),
      success: (validated) => tr('welcome', {username: validated.name}),
      error: tr('wrong'),
      finally() {
        setIsLoading(false);
      },
    });
  }

  useEffect(() => {
    if (errors?.request_track_id && errors?.request_track_id?.type === "required") {
      toast.warning(tr('selTrack'));
    }
  }, [errors?.request_track_id, tr])

  return (
    <div className={`flex justify-center items-center ${styles.div}`}>
      <form onSubmit={handleSubmit(onSubmit)} className={`flex justify-center items-center flex-col p-7 mx-4 gap-4 w-full max-w-md bg-[#ebe7e721] border-2 border-solid border-[#c5c3c34a] rounded-lg ${styles.form}`}>
        {
          siteImage && <Image src={siteImage} alt='Team Bdaya' width={150} height={0} loading='eager' unoptimized />
        }
        <h2 className='text-white text-2xl'>{tr('register')}</h2>
        {!canRegister ? <h1 className="text-white text-2xl">Register is Closed for Now</h1> :
          <>
            <Box className="flex gap-4 justify-center items-center w-full">
              <EmailOutlinedIcon sx={{ color: "white" }} />
              <TextField
                {...register("email", {
                  required: true,
                  pattern: {
                    value: /^[A-Z0-9._-]+@gmail\.com$/i,
                    message: tr('invalidGmail')
                  }
                })}
                variant='filled'
                type='email'
                inputMode='email'
                autoComplete='email'
                label={tr('email')}
                error={!!errors.email}
                helperText={errors?.email?.message}
                fullWidth
                required
                sx={{ bgcolor: "whitesmoke", borderRadius: "0.5rem" }}
              />
            </Box>
            <Box className="flex gap-4 justify-center items-center w-full">
              <PersonOutlineOutlinedIcon sx={{ color: "white" }} />
              <TextField
                {...register("name", { required: true })}
                variant='filled'
                autoComplete='name'
                label={tr('name')}
                fullWidth
                required
                sx={{ bgcolor: "whitesmoke", borderRadius: "0.5rem" }}
              />
            </Box>
            <Box className='flex gap-4 justify-center items-center w-full'>
              <AssignmentIndOutlinedIcon sx={{ color: "white" }} />
              <TextField
                {...register("collage_code", { required: true, pattern: { value: /^[CMA]\d{7}$/g, message: "This is Not a Valid Code" } })}
                variant='filled'
                label={tr('collage')}
                fullWidth
                required
                error={!!errors.collage_code}
                helperText={errors?.collage_code?.message}
                sx={{ bgcolor: "whitesmoke", borderRadius: "0.5rem" }}
              />
            </Box>
            <Box className='flex gap-4 justify-center items-center w-full'>
              <PhoneOutlinedIcon sx={{ color: "white" }} />
              <TextField
                {...register("phone_number", { required: true,})}
                variant='filled'
                inputMode='tel'
                type='tel'
                label={tr('phone')}
                fullWidth
                error={!!errors.phone_number}
                helperText={errors?.phone_number?.message}
                required
                sx={{ bgcolor: "whitesmoke", borderRadius: "0.5rem" }}
              />
            </Box>
            <Box className='flex gap-4 justify-center items-center w-full'>
              <LocationSearchingOutlinedIcon sx={{ color: "white" }} />
              <FormControl fullWidth variant='filled' error={!!errors.request_track_id} required>
                <InputLabel id="Track-label" title='track to enter'>{tr('track')}</InputLabel>
                <Select
                  {...register("request_track_id", { required: true })}
                  id="Track"
                  labelId='Track-label'
                  variant='filled'
                  required
                  sx={{ bgcolor: "whitesmoke", borderRadius: "0.5rem" }}
                >
                  {tracks.length > 0 ? tracks.map(track => <MenuItem value={track.id} key={track.id}>{track.track}</MenuItem>) : null}
                </Select>
              </FormControl>
            </Box>
            <Link href="login" className='text-white'>{tr('haveAcc')}</Link>
            <Button type='submit' fullWidth variant='contained' loadingPosition='start' loading={isLoading}>{tr('register')}</Button>
          </>
        }
      </form>
    </div>
  )
}
