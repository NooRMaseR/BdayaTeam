'use client';

import TextField  from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';

import EmailOutlinedIcon from '@mui/icons-material/EmailOutlined';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';

import { useAppDispatch, useAppSelector } from '../../utils/hooks';
import type { components } from '../../generated/api_types';
import PasswordField from '../../components/password';
import { setCredentials } from '../../utils/states';
import { Link, useRouter } from '@/i18n/navigation';
import { API } from '../../utils/api.client';
import { useTranslations } from 'next-intl';
import { useForm } from 'react-hook-form';
import styles from "./login.module.css";
import { useState } from 'react';
import { toast } from 'sonner';
import Image from 'next/image';



type GetLogIn = components['schemas']['Login'];
type SendLogIn = components['schemas']['loginRequest'];

export default function LogInForm() {
  const { handleSubmit, register, formState: { errors } } = useForm<SendLogIn>();
  const siteImage = useAppSelector(state => state.settings.site_image);
  const [isLoading, setIsloading] = useState<boolean>(false);
  const tr = useTranslations('loginPage');
  const dispatch = useAppDispatch();
  const router = useRouter();

  const onSubmit = async (data: SendLogIn) => {
    setIsloading(true);
    const loginSubmit = async () => {
      const { response, data: body, error } = await API.POST("/api/login/", { body: data });

      if (response.ok && body) {
        return await Promise.resolve(body);
      } else {
        return await Promise.reject(error);
      };
    }

    toast.promise<GetLogIn>(loginSubmit(),
      {
        loading: tr('loading'),
        success(data) {
          dispatch(setCredentials({ isLoading: false, isAuthed: true, user: data }));
          switch (data.role) {
            case "organizer":
              router.replace(`/${data.role}`);
              break;
              
            default:
              router.replace(`/${data.role}/${data.track?.track}`);
              break;
          };
          return tr("welcome", {username: data.username})
        },
        error: tr('invalid'),
        finally() {
          setIsloading(false);
        },
      }
    )
  }

  return (
    <div className={`flex justify-center items-center ${styles.div}`}>
      <form onSubmit={handleSubmit(onSubmit)} className={`flex justify-center items-center flex-col p-7 mx-4 gap-4 w-full max-w-md bg-[#ebe7e721] border-2 border-solid border-[#c5c3c34a] rounded-lg ${styles.form}`}>
        {
          siteImage
            ? <Link href="/">
            <Image src={siteImage} alt='Team Bdaya' width={150} height={150} loading='eager' unoptimized />
            </Link>
            : null
        }
        <h2 className='text-white text-2xl'>{tr('login')}</h2>
        <Box className="flex gap-4 justify-center items-center" sx={{ width: "100%" }}>
          <EmailOutlinedIcon sx={{ color: "white" }} />
          <TextField
            {...register(
              "email", {
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
            label={`${tr('email')}`}
            error={!!errors.email}
            helperText={errors.email?.message}
            fullWidth
            required
            sx={{ bgcolor: "whitesmoke", borderRadius: "0.5rem" }}
          />
        </Box>
        <Box className='flex gap-4 justify-center items-center' sx={{ width: "100%" }}>
          <LockOutlinedIcon sx={{ color: "white" }} />
          <PasswordField {...register("password", { required: true, minLength: 8 })}/>
        </Box>
        <Link href="register" className='text-white'>{tr('noAcc')}</Link>
        <Button type='submit' fullWidth variant='contained' loadingPosition='start' loading={isLoading}>{tr('login')}</Button>
      </form>
    </div>
  )
}

