'use client';

import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Skeleton from '@mui/material/Skeleton';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';

import { getHomeUrl } from "../utils/api.client";
import { useAuthStore } from '../utils/store';
import { useTranslations } from 'next-intl';
import NormalAnimation from './animations';
import { Link } from '@/i18n/navigation';

export default function NavButtons() {
    const isLoading = useAuthStore(state => state.isLoading);
    const isAuthed = useAuthStore(state => state.isAuthed);
    const user = useAuthStore(state => state.user);
    const tr = useTranslations('homePage');
    const link = getHomeUrl(user);

    if (isLoading) {
        return (
            <Box sx={{display: "flex", gap: "1rem"}}>
                <Skeleton variant='rounded' width={150} height={50} />
                <Skeleton variant='rounded' width={150} height={50} />
            </Box>
        )
    };

    if (isAuthed) {
        return (
            <NormalAnimation component='div' initial={{opacity: 0, y: 50}} animate={{opacity: 1, y: 0}}>
                <Link href={link}>
                    <Button
                        variant="outlined"
                        size="large"
                        sx={{ borderRadius: '50px', borderColor: 'white', color: 'white' }}
                    >
                        {tr('homePage')}
                    </Button>
                </Link>
            </NormalAnimation>
        );
    };
    return (
        <>
            <Link href='/register'>
                <Button
                    variant="contained"
                    size="large"
                    color="secondary"
                    endIcon={<ArrowForwardIcon />}
                    sx={{ borderRadius: '50px' }}
                >
                    {tr('register')}
                </Button>
            </Link>
            <Link href='/login'>
                <Button
                    variant="outlined"
                    size="large"
                    sx={{ borderRadius: '50px', borderColor: 'white', color: 'white' }}
                >
                    {tr('login')}
                </Button>
            </Link>
        </>
    )
}
