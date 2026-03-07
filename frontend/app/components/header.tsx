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

import { useAuthStore, useSettingsStore } from '@/app/utils/store';
import { Link, useRouter } from '@/i18n/navigation';
import LanguageSwitcher from './language_switcher';
import { getHomeUrl } from "../utils/api.client";
import { useTranslations } from 'next-intl';
import API from '@/app/utils/api.client';
import { Box } from '@mui/material';
import { useState } from 'react';
import Image from 'next/image';


export default function Header() {
  const isAuthed = useAuthStore((state) => state.isAuthed);
  const user = useAuthStore((state) => state.user);
  const site_image = useSettingsStore((state) => state.site_image);
  const logout = useAuthStore(state => state.logout)
  const [drawerOpen, setDrawerOpen] = useState<boolean>(false);
  const tr = useTranslations('header');
  const url = getHomeUrl(user);
  const router = useRouter();


  const openDrawer = () => setDrawerOpen(true);
  const closeDrawer = () => setDrawerOpen(false);

  const logoutF = async () => {
    const { response } = await API.GET("/api/logout/");
    if (response.ok) {
      logout();
      router.replace("/login");
    }
  }

  return (
    <AppBar sx={{ bgcolor: "#193cb8" }}>
      <Toolbar component='nav' sx={{ display: 'flex', justifyContent: "space-between" }}>
        <Link href="/">
          {
            site_image
              ? <Box sx={{ width: "100px", height: "50px", position: "relative" }} >
                <Image src={site_image} alt='Team Bdaya' loading='eager' fill unoptimized />
              </Box>
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
                <>
                  <ListItem sx={{ display: { xs: "none", sm: "flex", width: "max-content" }, gap: '1rem' }}>
                    <Link href={url}>
                      <Button sx={{ width: "max-content" }} id='Home-Button' variant='contained'>{tr('home')}</Button>
                    </Link>
                    <Button sx={{ width: "max-content" }} variant='contained' onClick={logoutF}>{tr('logout')}</Button>
                  </ListItem>

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
                </>
              )
              : null
          }
        </List>
      </Toolbar>
    </AppBar>
  );
}
