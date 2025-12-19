'use client';

import { Box, Button, FormControl, InputLabel, MenuItem, Select, TextField } from '@mui/material';
import LocationSearchingOutlinedIcon from '@mui/icons-material/LocationSearchingOutlined';
import { GetRegister, SendRegister, Track, UserRole } from '../utils/api_types_helper';
import PersonOutlineOutlinedIcon from '@mui/icons-material/PersonOutlineOutlined';
import AssignmentIndOutlinedIcon from '@mui/icons-material/AssignmentIndOutlined';
import PhoneOutlinedIcon from '@mui/icons-material/PhoneOutlined';
import EmailOutlinedIcon from '@mui/icons-material/EmailOutlined';
import { setCredentials } from '../utils/states';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import styles from "./register.module.css";
import { useDispatch } from 'react-redux';
import { useForm } from 'react-hook-form';
import serverApi from '../utils/api';
import Link from 'next/link';


export default function RegisterPage() {
  const { handleSubmit, register } = useForm<SendRegister>();
  const [tracks, setTracks] = useState<Track[]>([] as Track[])
  const dispatch = useDispatch();
  const router = useRouter();

  const onSubmit = async (data: SendRegister) => {

    const res = await serverApi<GetRegister>(
      "POST",
      "/register/",
      data
    );

    if (res.success && res.data) {
      dispatch(setCredentials({ isLoading: false, isAuthed: true, user: {username: res.data.name, role: UserRole.MEMBER, track: res.data.track} }));
      router.replace(`/member/${res.data.track?.track}`);
    } else {
      console.table(res.error);
    };
  }

  useEffect(() => {
    const req = async () => {
      const res = await serverApi<Track[]>("GET", "/tracks/");
      if (res.success && res.data) {
        setTracks(res.data);
      }
    }
    req();
   }, []);


  return (
    <div className={`flex justify-center items-center ${styles.div}`}>
      <form onSubmit={handleSubmit(onSubmit)} className={`flex justify-center items-center flex-col p-7 gap-4 w-full max-w-md ${styles.form}`}>
        <h1 className='text-white text-3xl font-bold'>Team Bdaya</h1>
        <h2 className='text-white text-2xl'>Welcome To Team Bdaya</h2>
        <Box className="flex gap-4 justify-center items-center w-full">
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
            {...register("collage_code", { required: true })}
            variant='filled'
            label="Collage Code"
            fullWidth
            required
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
        <Button type='submit' fullWidth variant='contained'>Submit</Button>
      </form>
    </div>
  )
}

