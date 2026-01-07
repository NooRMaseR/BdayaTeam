"use client";

import { Button } from '@mui/material';
import { logout } from '@/app/utils/states';
import { useRouter } from 'next/navigation';
import { API } from '@/app/utils/api.client';
import { useAppDispatch } from '@/app/utils/hooks';

export default function LogoutBtn() {

  const router = useRouter();
  const dispatch = useAppDispatch();

  const logoutF = async () => {
    const {response} = await API.GET("/logout/");
    if (response.ok) {
      dispatch(logout());
      router.replace("/login");
    }
  }

  
  return (
    <Button variant='contained' onClick={logoutF}>Logout</Button>
  )
}
