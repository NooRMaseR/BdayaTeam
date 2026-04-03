'use client';

import LocationSearchingOutlinedIcon from '@mui/icons-material/LocationSearchingOutlined';
import PersonOutlineOutlinedIcon from '@mui/icons-material/PersonOutlineOutlined';
import AssignmentIndOutlinedIcon from '@mui/icons-material/AssignmentIndOutlined';
import PhoneOutlinedIcon from '@mui/icons-material/PhoneOutlined';
import EmailOutlinedIcon from '@mui/icons-material/EmailOutlined';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';

import { useAuthStore, useSettingsStore } from '../../utils/store';
import LocaledTextField from '@/app/components/localed_textField';
import type { components } from '../../generated/api_types';
import API, { formatTime } from '../../utils/api.client';
import { Link, useRouter } from '@/i18n/navigation';
import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import styles from "./register.module.css";
import { useForm } from 'react-hook-form';
import { toast } from 'sonner';
import Image from 'next/image';

type RegisterFormProps = {
  tracks: components['schemas']['SimpleTrackSchema'][];
  canRegister?: boolean | null
}

type SendRegister = components['schemas']['RegisterRequest'];

export default function RegisterForm({ tracks, canRegister = false }: RegisterFormProps) {
  const { handleSubmit, register, setError, formState: { errors } } = useForm<SendRegister>({ defaultValues: { phone_number: "+20" } });
  const siteImage = useSettingsStore(state => state.site_image);
  const setCredentials = useAuthStore(state => state.setCredentials);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const tr = useTranslations('registerPage');
  const router = useRouter();

  const onSubmit = async (data: SendRegister) => {
    setIsLoading(true);
    const submitRegister = async () => {
      const editedData = data;
      editedData.collage_code = editedData.collage_code.toUpperCase();

      if (!editedData.phone_number.startsWith("+2")) {
        editedData.phone_number = `+2${editedData.phone_number}`;
      }

      const { data: body, error, response } = await API.POST(
        "/api/register/",
        {
          body: editedData
        },
      );

      if (response.ok && body) {
        setCredentials({ isLoading: false, isAuthed: true, user: { username: body.name, role: "member", track: body.track, is_admin: false } });
        router.replace(`/member/${body.track?.name}`);
        return await Promise.resolve(body);
      } else if (error) {
        if (response.status === 422 && typeof error.detail[0] !== "string") {
          setError(error.detail[0].loc[error.detail[0].loc.length - 1] as keyof SendRegister, { message: error.detail[0].ctx.error });
        } else if (response.status === 400 && error) {
          Object.entries(error).forEach(er => {
            setError(er[0] as keyof SendRegister, { message: er[1] });
          });
        } else if (response.status === 429) {
          const time = formatTime(parseInt(response.headers.get("Retry-After") ?? '0'));
          toast.warning(tr('blocked', {duration: time.duration, unit: tr(time.unit)}), { duration: 5000 });
        }
        return await Promise.reject();
      };
    };

    toast.promise(submitRegister(), {
      loading: tr('loading'),
      success: (validated) => validated ? tr('welcome', { username: validated.name }) : "no name detected",
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
      <form
        onSubmit={handleSubmit(onSubmit)}
        className={`flex justify-center items-center flex-col p-8 mx-4 gap-5 w-full max-w-md dark:bg-slate-900/90 backdrop-blur-md border border-gray-200 dark:border-slate-700 shadow-2xl rounded-xl transition-colors duration-300 ${styles.form}`}
      >
        {
          siteImage && (
            <Image
              src={siteImage}
              alt='Team Bdaya'
              width={150}
              height={0}
              loading='eager'
              unoptimized
              className="dark:brightness-90 transition-all duration-300"
            />
          )
        }

        <h2 className='text-2xl font-bold text-white'>
          {tr('register')}
        </h2>

        {!canRegister ? (
          <h1 className="text-xl font-bold text-red-600 dark:text-red-400 mt-4 text-center">
            {tr("regClosed")}
          </h1>
        ) : (
          <>
            <Box className="flex gap-4 justify-center items-center w-full">
              <EmailOutlinedIcon sx={{ color: 'white' }} />
              <LocaledTextField
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
                sx={{ borderRadius: "0.5rem", ".MuiInputLabel-root": { color: "#d9d9d9" }, "input": { color: "white" } }}
              />
            </Box>

            <Box className="flex gap-4 justify-center items-center w-full">
              <PersonOutlineOutlinedIcon sx={{ color: "white" }} />
              <LocaledTextField
                {...register("name", { required: true })}
                variant='filled'
                autoComplete='name'
                label={tr('name')}
                fullWidth
                required
                sx={{ borderRadius: "0.5rem", ".MuiInputLabel-root": { color: "#d9d9d9" }, "input": { color: "white" } }}
              />
            </Box>

            <Box className='flex gap-4 justify-center items-center w-full'>
              <AssignmentIndOutlinedIcon sx={{ color: "white" }} />
              <LocaledTextField
                {...register("collage_code", { required: true, pattern: { value: /^[MCAE]\d+$/i, message: "invalid collage code" } })}
                variant='filled'
                label={tr('collage')}
                fullWidth
                required
                error={!!errors.collage_code}
                helperText={errors?.collage_code?.message}
                sx={{ borderRadius: "0.5rem", ".MuiInputLabel-root": { color: "#d9d9d9" }, "input": { color: "white" } }}
              />
            </Box>

            <Box className='flex gap-4 justify-center items-center w-full'>
              <PhoneOutlinedIcon sx={{ color: "white" }} />
              <LocaledTextField
                {...register("phone_number", { required: true, })}
                variant='filled'
                inputMode='tel'
                type='tel'
                label={tr('phone')}
                fullWidth
                error={!!errors.phone_number}
                helperText={errors?.phone_number?.message}
                required
                sx={{ borderRadius: "0.5rem", ".MuiInputLabel-root": { color: "#d9d9d9" }, "input": { color: "white" } }}
              />
            </Box>

            <Box className='flex gap-4 justify-center items-center w-full'>
              <LocationSearchingOutlinedIcon sx={{ color: "white" }} />
              <FormControl fullWidth variant='filled' error={!!errors.request_track_id} required>
                <InputLabel id="Track-label" title='track to enter' sx={{ color: "#d9d9d9", "input": { color: "white" } }}>{tr('track')}</InputLabel>
                <Select
                  {...register("request_track_id", { required: true })}
                  id="Track"
                  labelId='Track-label'
                  variant='filled'
                  required
                  sx={{ borderRadius: "0.5rem", ".MuiInputLabel-root": { color: "#d9d9d9" }, "input": { color: "white" } }}
                >
                  {tracks.length > 0 ? tracks.map(track => <MenuItem value={track.id} key={track.id}>{track.name}</MenuItem>) : null}
                </Select>
              </FormControl>
            </Box>

            <Link
              href="login"
              className='text-sm font-medium text-white'
            >
              {tr('haveAcc')}
            </Link>

            <Button
              type='submit'
              fullWidth
              variant='contained'
              loadingPosition='start'
              loading={isLoading}
              sx={{ mt: 1, py: 1.5, borderRadius: '0.5rem', fontWeight: 'bold' }}
            >
              {tr('register')}
            </Button>
          </>
        )}
      </form>
    </div>
  )
}