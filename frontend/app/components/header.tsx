"use client";

import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import MenuIcon from "@mui/icons-material/Menu";
import ListItem from '@mui/material/ListItem';
import Toolbar from '@mui/material/Toolbar';
import AppBar from '@mui/material/AppBar';
import Drawer from '@mui/material/Drawer';
import Button from '@mui/material/Button';
import List from '@mui/material/List';

import { useAppDispatch, useAppSelector } from '@/app/utils/hooks';
import { Link, useRouter } from '@/i18n/navigation';
import LanguageSwitcher from './language_switcher';
import { API } from '@/app/utils/api.client';
import { useTranslations } from 'next-intl';
import { logout } from '@/app/utils/states';
import { useState } from 'react';
import Image from 'next/image';


export default function Header() {
  const { isAuthed, user } = useAppSelector((state) => state.auth);
  const site_image = useAppSelector((state) => state.settings.site_image);
  const [drawerOpen, setDrawerOpen] = useState<boolean>(false);
  const url = user?.role === "member" || user?.role === 'technical' ? `/${user?.role}/${user?.track?.track}` : `/${user?.role}`;
  const tr = useTranslations('header');
  const dispatch = useAppDispatch();
  const router = useRouter();


  const openDrawer = () => setDrawerOpen(true);
  const closeDrawer = () => setDrawerOpen(false);

  const logoutF = async () => {
    const { response } = await API.GET("/api/logout/");
    if (response.ok) {
      dispatch(logout());
      router.replace("/login");
    }
  }

  return (
    <AppBar sx={{ bgcolor: "#193cb8" }}>
      <Toolbar component='nav' sx={{ display: 'flex', justifyContent: "space-between" }}>
        <Link href="/">
          {
            site_image
              ? <Image src={site_image} alt='Team Bdaya' loading='eager' width={100} height={50} unoptimized />
              : <Typography component='h5' variant='h5'>{tr('teamBdaya')}</Typography>
          }
        </Link>
        <List sx={{ display: 'flex', justifyContent: "space-between" }}>
          <ListItem>
            <LanguageSwitcher />
          </ListItem>
          {
            isAuthed
              ? (
                <ListItem sx={{ display: { xs: "none", sm: "flex", width: "max-content" }, gap: '1rem' }}>
                  <Link href={url}>
                  <Button sx={{width: "max-content"}} id='Home-Button' variant='contained'>{tr('home')}</Button>
                  </Link>
                <Button sx={{width: "max-content"}} variant='contained' onClick={logoutF}>{tr('logout')}</Button>
                </ListItem>
              )
              : null
          }
          {
            isAuthed
              ? (
                <ListItem sx={{ display: { xs: 'block', sm: 'none', paddingInline: 0 } }}>
                  <IconButton onClick={openDrawer}>
                    <MenuIcon sx={{ color: 'white' }} />
                  </IconButton>
                  <Drawer open={drawerOpen} keepMounted onClose={closeDrawer} anchor='right'>
                    <List>
                      <ListItem>
                        <Link href={url}>
                          <Button id='Home-Button'>{tr('home')}</Button>
                        </Link>
                      </ListItem>
                      <ListItem>
                        <Button onClick={logoutF}>{tr('logout')}</Button>
                      </ListItem>
                    </List>
                  </Drawer>
                </ListItem>
              )
              : null
          }
        </List>
      </Toolbar>
    </AppBar>
  );
}
