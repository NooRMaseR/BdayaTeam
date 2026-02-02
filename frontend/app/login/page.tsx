'use client';

import EmailOutlinedIcon from '@mui/icons-material/EmailOutlined';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import { useAppDispatch, useAppSelector } from '../utils/hooks';
import type { components } from '../generated/api_types';
import { Box, Button, TextField } from '@mui/material';
import PasswordField from '../components/password';
import { setCredentials } from '../utils/states';
import { useRouter } from 'next/navigation';
import { API } from '../utils/api.client';
import { useForm } from 'react-hook-form';
import styles from "./login.module.css";
import { useState } from 'react';
import { toast } from 'sonner';
import Image from 'next/image';
import Link from 'next/link';

type GetLogIn = components['schemas']['Login'];
type SendLogIn = components['schemas']['loginRequest'];

export default function LogIn() {
  const { handleSubmit, register, formState: { errors } } = useForm<SendLogIn>();
  const siteImage = useAppSelector(state => state.settings.site_image);
  const [isLoading, setIsloading] = useState<boolean>(false);
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
        loading: "Loading....",
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
          return `Welcome Back ${data.username}`
        },
        error: "Invalid Email or Password",
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
            ? <Image src={siteImage} alt='Team Bdaya' width={150} height={150} loading='eager' unoptimized />
            : null
        }
        <h2 className='text-white text-2xl'>Login</h2>
        <Box className="flex gap-4 justify-center items-center" sx={{ width: "100%" }}>
          <EmailOutlinedIcon sx={{ color: "white" }} />
          <TextField
            {...register(
              "email", {
              required: true,
              pattern: {
                value: /^[A-Z0-9._-]+@gmail\.com$/i,
                message: "Invalid Gmail Email address"
              }
            })}
            variant='filled'
            type='email'
            inputMode='email'
            autoComplete='email'
            label="Email..."
            error={!!errors.email}
            helperText={errors.email?.message}
            fullWidth
            required
            sx={{ bgcolor: "whitesmoke", borderRadius: "0.5rem" }}
          />
        </Box>
        <Box className='flex gap-4 justify-center items-center' sx={{ width: "100%" }}>
          <LockOutlinedIcon sx={{ color: "white" }} />
          <PasswordField {...register("password", { required: true, minLength: 8 })} />
        </Box>
        <Link href="/register" className='text-white'>Don&apos;t have account?</Link>
        <Button type='submit' fullWidth variant='contained' loadingPosition='start' loading={isLoading}>Submit</Button>
      </form>
    </div>
  )
}

