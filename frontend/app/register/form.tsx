'use client';

import { Box, Button, FormControl, InputLabel, MenuItem, Select, TextField } from '@mui/material';
import LocationSearchingOutlinedIcon from '@mui/icons-material/LocationSearchingOutlined';
import PersonOutlineOutlinedIcon from '@mui/icons-material/PersonOutlineOutlined';
import AssignmentIndOutlinedIcon from '@mui/icons-material/AssignmentIndOutlined';
import PhoneOutlinedIcon from '@mui/icons-material/PhoneOutlined';
import EmailOutlinedIcon from '@mui/icons-material/EmailOutlined';
import { useAppDispatch, useAppSelector } from '../utils/hooks';
import type { components } from '../generated/api_types';
import { setCredentials } from '../utils/states';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import styles from "./register.module.css";
import { useForm } from 'react-hook-form';
import { API } from '../utils/api.client';
import { toast } from 'sonner';
import Image from 'next/image';
import Link from 'next/link';

type RegisterFormProps = {
  tracks: components['schemas']['Track'][];
  canRegister?: boolean | null
}

type SendRegister = components['schemas']['RegisterMemberRequest'];

export default function RegisterForm({ tracks, canRegister = false }: RegisterFormProps) {
  const { handleSubmit, register, setError, formState: { errors } } = useForm<SendRegister>();
  const siteImage = useAppSelector(state => state.settings.site_image);
  const [isLoading, setIsLoading] = useState<boolean>(false);
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
      loading: "Loading....",
      success: (validated) => `Welcome ${validated.name}, Your password will be sent via email soon`,
      error: "Somthing Went Wrong, Try again",
      finally() {
        setIsLoading(false);
      },
    });
  }

  useEffect(() => {
    if (errors?.request_track_id && errors?.request_track_id?.type === "required") {
      toast.warning("Please Select A Valid Track");
    }
  }, [errors?.request_track_id])

  return (
    <div className={`flex justify-center items-center ${styles.div}`}>
      <form onSubmit={handleSubmit(onSubmit)} className={`flex justify-center items-center flex-col p-7 mx-4 gap-4 w-full max-w-md bg-[#ebe7e721] border-2 border-solid border-[#c5c3c34a] rounded-lg ${styles.form}`}>
        {
          siteImage
            ? <Image src={siteImage} alt='Team Bdaya' width={150} height={0} loading='eager' unoptimized />
            : null
        }
        <h2 className='text-white text-2xl'>Register</h2>
        {!canRegister ? <h1 className="text-white text-2xl">Register is Closed for Now</h1> :
          <>
            <Box className="flex gap-4 justify-center items-center w-full">
              <EmailOutlinedIcon sx={{ color: "white" }} />
              <TextField
                {...register("email", {
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
                label="Name..."
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
                label="Collage Code"
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
                {...register("phone_number", { required: true })}
                variant='filled'
                inputMode='tel'
                type='tel'
                label="Phone Number"
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
                <InputLabel id="Track-label" title='track to enter'>Track</InputLabel>
                <Select
                  {...register("request_track_id", { required: true })}
                  id="Track"
                  labelId='Track-label'
                  variant='filled'
                  label="Track"
                  required
                  sx={{ bgcolor: "whitesmoke", borderRadius: "0.5rem" }}
                >
                  {tracks.length > 0 ? tracks.map(track => <MenuItem value={track.id} key={track.id}>{track.track}</MenuItem>) : null}
                </Select>
              </FormControl>
            </Box>
            <Link href="/login" className='text-white'>Alraedy have account?</Link>
            <Button type='submit' fullWidth variant='contained' loadingPosition='start' loading={isLoading}>Submit</Button>
          </>
        }
      </form>
    </div>
  )
}
