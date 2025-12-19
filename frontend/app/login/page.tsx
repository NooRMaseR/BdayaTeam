'use client';

import { GetLogIn, SendLogIn, UserRole } from '../utils/api_types_helper';
import EmailOutlinedIcon from '@mui/icons-material/EmailOutlined';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import { Box, Button, TextField } from '@mui/material';
import { setCredentials } from '../utils/states';
import { useRouter } from 'next/navigation';
import { useDispatch } from 'react-redux';
import { useForm } from 'react-hook-form';
import styles from "./login.module.css";
import serverApi from '../utils/api';
import Link from 'next/link';


export default function LogIn() {
  const { handleSubmit, register } = useForm<SendLogIn>();
  const dispatch = useDispatch();
  const router = useRouter();

  const onSubmit = async (data: SendLogIn) => {

    const res = await serverApi<GetLogIn>(
      "POST",
      "/login/",
      data
    );

    if (res.success && res.data) {
      dispatch(setCredentials({ isLoading: false, isAuthed: true, user: res.data }));
      switch (res.data.role) {
        case UserRole.MEMBER:
          router.replace(`/${res.data.role}/${res.data.track?.track}`);
          break;
          
          default:
          router.replace(`/${res.data.role}`);
          break;
      }
    } else {
      console.table(res.error);
    };
  }


  return (
    <div className={`flex justify-center items-center ${styles.div}`}>
      <form onSubmit={handleSubmit(onSubmit)} className={`flex justify-center items-center flex-col gap-4 ${styles.form}`}>
        <h1 className='text-white text-3xl font-bold'>Bdaya Team</h1>
        <h2 className='text-white text-2xl'>Welcome Back</h2>
        <Box className="flex gap-4 justify-center items-center" sx={{ width: "100%" }}>
          <EmailOutlinedIcon sx={{ color: "white" }} />
          <TextField
            {...register("email", { required: true })}
            variant='filled'
            type='email'
            inputMode='email'
            autoComplete='email'
            label="Email..."
            fullWidth
            required
            sx={{ bgcolor: "whitesmoke", borderRadius: "0.5rem" }}
          />
        </Box>
        <Box className='flex gap-4 justify-center items-center' sx={{ width: "100%" }}>
          <LockOutlinedIcon sx={{ color: "white" }} />
          <TextField
            {...register("password", { required: true })}
            variant='filled'
            type='password'
            autoComplete='password'
            label="password"
            fullWidth
            required
            sx={{ bgcolor: "whitesmoke", borderRadius: "0.5rem" }}
          />
        </Box>
        <Link href="/register" className='text-white'>Don't have account?</Link>
        <Button type='submit' fullWidth variant='contained'>Submit</Button>
      </form>
    </div>
  )
}

