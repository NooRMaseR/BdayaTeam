"use client";

import { UserRole } from '@/app/utils/api_types_helper';
import bdayaImage from "../../static/bdaya_croped.png";
import { useAppSelector } from '@/app/utils/hooks';
import { Button, Skeleton } from '@mui/material';
import NormalAnimation from '../animations';
import LogoutBtn from './logout_btn';
import Image from 'next/image';
import Link from 'next/link';


export default function Header() {
  const { isLoading, isAuthed, user } = useAppSelector((state) => state.auth);
  const url = user?.role == UserRole.MEMBER ? `/member/${user.track?.track}` : `/${user?.role}`;

  if (isLoading) {
    return (
      <Skeleton variant='rectangular' width={"100%"} height={70} animation="wave" sx={{backgroundColor: "#193cb8", position: "sticky", top: 0, left: 0, zIndex: 50}} />
    )
  }
  if (!isAuthed) {
    return null;
  };

  return (
    <header className="sticky top-0 left-0 w-full bg-blue-800 shadow-md z-50">
      <nav className="px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center pt-1 pb-4">
          <NormalAnimation component="div" initial={{ opacity: 0, y: -50 }} animate={{ opacity: 1, y: 0 }} className="text-white text-lg font-bold">
            <Link href="/">
              <Image src={bdayaImage} alt="Bdaya Logo" width={100} height={10} />
            </Link>
          </NormalAnimation>
          <ol className="flex items-center gap-4">
            <NormalAnimation component='li' initial={{ opacity: 0, y: -50 }} animate={{ opacity: 1, y: 0 }} className='flex gap-4'>
              <Link href={url}>
                <Button variant='contained'>Home</Button>
              </Link>
              <LogoutBtn />
            </NormalAnimation>
          </ol>
        </div>
      </nav>
    </header>
  );
}
