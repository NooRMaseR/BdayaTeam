'use client';

import type { GetLogIn, SendLogIn } from '../utils/api_types_helper';
import EmailOutlinedIcon from '@mui/icons-material/EmailOutlined';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import { Box, Button, TextField } from '@mui/material';
import PasswordField from '../components/password';
import { setCredentials } from '../utils/states';
import { useRouter } from 'next/navigation';
import { API } from '../utils/api.client';
import { useDispatch } from 'react-redux';
import { useForm } from 'react-hook-form';
import styles from "./login.module.css";
import { toast } from 'sonner';
import Image from 'next/image';
import Link from 'next/link';


export default function LogIn() {
  const { handleSubmit, register, formState: { errors } } = useForm<SendLogIn>();
  const dispatch = useDispatch();
  const router = useRouter();

  const onSubmit = async (data: SendLogIn) => {
    const loginSubmit = async () => {
      const { response, data: body, error } = await API.POST("/login/", { body: data });

      if (response.ok && body) {
        return await Promise.resolve(body);
      } else {
        return await Promise.reject(error);
      };
    }

    toast.promise<GetLogIn>(loginSubmit(),
      {
        loading: "Loading....",
        success: (data) => {
          dispatch(setCredentials({ isLoading: false, isAuthed: true, user: data }));
          switch (data.role) {
            case "member":
              router.replace(`/${data.role}/${data.track?.track}`);
              break;

            default:
              router.replace(`/${data.role}`);
              break;
          };
          return `Welcome Back ${data.username}`
        },
        error: "Invalid Email or Password"
      }
    )
  }


  return (
    <div className={`flex justify-center items-center ${styles.div}`}>
      <form onSubmit={handleSubmit(onSubmit)} className={`flex justify-center items-center flex-col p-7 mx-4 gap-4 w-full max-w-md bg-[#ebe7e721] border-2 border-solid border-[#c5c3c34a] rounded-lg ${styles.form}`}>
        <Image src="/bdaya_croped.png" alt='Team Bdaya' width={150} height={0} />
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
        <Link href="/register" className='text-white'>Don't have account?</Link>
        <Button type='submit' fullWidth variant='contained'>Submit</Button>
      </form>
    </div>
  )
}

