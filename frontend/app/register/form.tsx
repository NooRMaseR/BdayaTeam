'use client';

import { Box, Button, FormControl, InputLabel, MenuItem, Select, TextField } from '@mui/material';
import LocationSearchingOutlinedIcon from '@mui/icons-material/LocationSearchingOutlined';
import PersonOutlineOutlinedIcon from '@mui/icons-material/PersonOutlineOutlined';
import AssignmentIndOutlinedIcon from '@mui/icons-material/AssignmentIndOutlined';
import type { SendRegister, Track } from '../utils/api_types_helper';
import PhoneOutlinedIcon from '@mui/icons-material/PhoneOutlined';
import EmailOutlinedIcon from '@mui/icons-material/EmailOutlined';
import { setCredentials } from '../utils/states';
import { useRouter } from 'next/navigation';
import styles from "./register.module.css";
import { useDispatch } from 'react-redux';
import { useForm } from 'react-hook-form';
import { API } from '../utils/api.client';
import { toast } from 'sonner';
import Image from 'next/image';
import Link from 'next/link';

type RegisterFormProps = {
  tracks: Track[];
  canRegister: boolean
}

export default function RegisterForm({ tracks, canRegister }: RegisterFormProps) {
  const { handleSubmit, register, formState: { errors } } = useForm<SendRegister>();
  const dispatch = useDispatch();
  const router = useRouter();

  const onSubmit = async (data: SendRegister) => {
    const submitRegister = async () => {
      const { data: body, error, response } = await API.POST(
        "/register/",
        {
          body: data
        }
      );

      if (response.ok && body) {
        dispatch(setCredentials({ isLoading: false, isAuthed: true, user: { username: body.name, role: "member", track: body.track } }));
        router.replace(`/member/${body.track?.track}`);
        return await Promise.resolve(body);
      } else {
        console.error(error);
        return await Promise.reject();
      };
    };

    toast.promise(submitRegister(), {
      loading: "Loading....",
      success: (validated) => `Welcome ${validated.name}, Your password will be sent via email soon`,
      error: "Error Happend"
    })
  }

  return (
    <div className={`flex justify-center items-center ${styles.div}`}>
      <form onSubmit={handleSubmit(onSubmit)} className={`flex justify-center items-center flex-col p-7 mx-4 gap-4 w-full max-w-md bg-[#ebe7e721] border-2 border-solid border-[#c5c3c34a] rounded-lg ${styles.form}`}>
        <Image src="/bdaya_croped.png" alt='Team Bdaya' width={150} height={0} />
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
                required
                sx={{ bgcolor: "whitesmoke", borderRadius: "0.5rem" }}
              />
            </Box>
            <Box className='flex gap-4 justify-center items-center w-full'>
              <LocationSearchingOutlinedIcon sx={{ color: "white" }} />
              <FormControl fullWidth variant='filled'>
                <InputLabel id="Track-label">Track</InputLabel>
                <Select
                  {...register("request_track_id", { required: "Please Select a Track" })}
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
            <Button type='submit' fullWidth variant='contained'>Submit</Button>
          </>
        }
      </form>
    </div>
  )
}
