'use client';

import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import { Box, Button, Skeleton } from '@mui/material';
import { useAppSelector } from '@/app/utils/hooks';
import { useTranslations } from 'next-intl';
import NormalAnimation from './animations';
import { Link } from '@/i18n/navigation';

export default function NavButtons({locale}: {locale: string}) {
    const { isLoading, isAuthed, user } = useAppSelector(state => state.auth);
    const tr = useTranslations('homePage');
    const link = user?.role === "member" ? `/${user?.role}/${user?.track?.track}` : `/${user?.role}}`;
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
            <Link href={`/register`}>
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
            <Link href={`/login`}>
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
