"use client";

import { Button } from '@mui/material';
import serverApi from '@/app/utils/api';
import { logout } from '@/app/utils/states';
import { useRouter } from 'next/navigation';
import { useAppDispatch } from '@/app/utils/hooks';

export default function LogoutBtn() {

  const router = useRouter();
  const dispatch = useAppDispatch();

  const logoutF = async () => {
    const res = await serverApi("GET", "/logout/");
    if (res.success) {
      dispatch(logout());
      router.replace("/login");
    }
  }

  
  return (
    <Button variant='contained' onClick={logoutF}>Logout</Button>
  )
}
