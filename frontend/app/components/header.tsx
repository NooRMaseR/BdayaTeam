"use client";

import { useAppDispatch, useAppSelector } from '@/app/utils/hooks';
import { Button, Skeleton, Typography } from '@mui/material';
import { API } from '@/app/utils/api.client';
import { logout } from '@/app/utils/states';
import { useRouter } from 'next/navigation';
import NormalAnimation from './animations';
import Image from 'next/image';
import Link from 'next/link';


export default function Header() {
  const { isLoading, isAuthed, user } = useAppSelector((state) => state.auth);
  const site_image = useAppSelector((state) => state.settings.site_image);
  const url = user?.role === "member" || 'technical' ? `/${user?.role}/${user?.track?.track}` : `/${user?.role}`;
  const router = useRouter();
  const dispatch = useAppDispatch();

  if (isLoading) {
    return (
      <Skeleton variant='rectangular' width={"100%"} height={70} animation="wave" sx={{ backgroundColor: "#193cb8", position: "sticky", top: 0, left: 0, zIndex: 50 }} />
    )
  }
  if (!isAuthed) {
    return null;
  };

  const logoutF = async () => {
    const {response} = await API.GET("/api/logout/");
    if (response.ok) {
      dispatch(logout());
      router.replace("/login");
    }
  }

  return (
    <header className="sticky top-0 left-0 w-full bg-blue-800 shadow-md z-50">
      <nav className="px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <NormalAnimation component='div' initial={{ opacity: 0, y: -50 }} animate={{ opacity: 1, y: 0 }} className="text-white text-lg font-bold">
            <Link href="/">
              {
                site_image
                  ? <Image src={site_image} alt='Team Bdaya' loading='eager' width={100} height={50} unoptimized />
                  : <Typography variant='h3'>TeamBdaya</Typography>
              }
            </Link>
          </NormalAnimation>
          <ol className="flex items-center gap-4">
            <NormalAnimation component='li' initial={{ opacity: 0, y: -50 }} animate={{ opacity: 1, y: 0 }} className='flex gap-4'>
              <Link href={url}>
                <Button id='Home-Button' variant='contained'>Home</Button>
              </Link>
              <Button variant='contained' onClick={logoutF}>Logout</Button>
            </NormalAnimation>
          </ol>
        </div>
      </nav>
    </header>
  );
}
