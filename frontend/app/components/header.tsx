"use client";

import DialogContentText from '@mui/material/DialogContentText';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Dialog from '@mui/material/Dialog';

import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import MenuIcon from "@mui/icons-material/Menu";
import ListItem from '@mui/material/ListItem';
import Toolbar from '@mui/material/Toolbar';
import AppBar from '@mui/material/AppBar';
import Drawer from '@mui/material/Drawer';
import Button from '@mui/material/Button';
import List from '@mui/material/List';
import Box from '@mui/material/Box';

import { useAuthStore, useSettingsStore } from '@/app/utils/store';
import { Link, useRouter } from '@/i18n/navigation';
import LanguageSwitcher from './language_switcher';
import { getHomeUrl } from "../utils/api.client";
import { useTranslations } from 'next-intl';
import ThemeSwitcher from './themeSwitcher';
import API from '@/app/utils/api.client';
import { useState } from 'react';
import Image from 'next/image';

type LogoutDialogProps = {
  open: boolean;
  onSucces: () => void;
  onClose: () => void;
}

function LogoutDialog({ open, onSucces, onClose }: LogoutDialogProps) {
  const tr = useTranslations('header');

  return (
    <Dialog open={open}>
      <DialogTitle>{tr('logout')} {tr("?")}</DialogTitle>
      <DialogContent>
        <DialogContentText>{tr('logoutConf')}</DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button variant='contained' onClick={onClose}>{tr('cancel')}</Button>
        <Button variant='outlined' color='error' onClick={onSucces}>{tr('logout')}</Button>
      </DialogActions>
    </Dialog>
  )
}


export default function Header() {
  const isAuthed = useAuthStore((state) => state.isAuthed);
  const user = useAuthStore((state) => state.user);
  const site_image = useSettingsStore((state) => state.site_image);
  const logout = useAuthStore(state => state.logout);
  const [dlgOpen, setDlgOpen] = useState<boolean>(false);
  const [drawerOpen, setDrawerOpen] = useState<boolean>(false);
  const tr = useTranslations('header');
  const url = getHomeUrl(user);
  const router = useRouter();

  const openDrawer = () => setDrawerOpen(true);
  const closeDrawer = () => setDrawerOpen(false);

  const openLogoutConf = () => {
    closeDrawer();
    setDlgOpen(true);
  };
  const closeLogoutConf = () => setDlgOpen(false);

  const logoutF = async () => {
    const { response } = await API.GET("/api/logout/");
    if (response.ok) {
      logout();
      closeLogoutConf();
      router.replace("/login");
    }
  }

  return (
    <>
      <LogoutDialog open={dlgOpen} onSucces={logoutF} onClose={closeLogoutConf} />
      <AppBar className='color-trans dark:bg-(--dark-color)! bg-(--team-color)!'>
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
            <div className='flex'>
              <ListItem>
                <LanguageSwitcher />
              </ListItem>
              <ListItem>
                <ThemeSwitcher />
              </ListItem>
            </div>
            {
              isAuthed
                ? (
                  <>
                    <ListItem sx={{ display: { xs: "none", sm: "flex", width: "max-content" }, gap: '1rem' }}>
                      <Link href={url}>
                        <Button sx={{ width: "max-content" }} id='Home-Button' variant='contained'>{tr('home')}</Button>
                      </Link>
                      <Button sx={{ width: "max-content" }} variant='contained' onClick={openLogoutConf}>{tr('logout')}</Button>
                    </ListItem>

                    <ListItem sx={{ display: { xs: 'block', sm: 'none', paddingInline: 0 } }}>
                      <IconButton onClick={openDrawer}>
                        <MenuIcon sx={{ color: 'white' }} />
                      </IconButton>
                      <Drawer open={drawerOpen} keepMounted onClose={closeDrawer} anchor='right'>
                        <List>
                          <ListItem>
                            <Link href={url} onClick={closeDrawer}>
                              <Button id='Home-Button'>{tr('home')}</Button>
                            </Link>
                          </ListItem>
                          <ListItem>
                            <Button onClick={openLogoutConf}>{tr('logout')}</Button>
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
    </>
  );
}
