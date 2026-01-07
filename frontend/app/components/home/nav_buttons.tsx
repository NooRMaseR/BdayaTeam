'use client';

import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import { UserRole } from '@/app/utils/api_types_helper';
import { Box, Button, Skeleton } from '@mui/material'
import { useAppSelector } from '@/app/utils/hooks';
import { motion } from "motion/react";
import Link from 'next/link'

export default function NavButtons() {
    const { isLoading, isAuthed, user } = useAppSelector(state => state.auth);
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
            <motion.div initial={{opacity: 0, y: 50}} animate={{opacity: 1, y: 0}}>
                <Link href={user?.role == UserRole.MEMBER ? `/${user?.role}/${user?.track?.track}` : `/${user?.role}`}>
                    <Button
                        variant="outlined"
                        size="large"
                        sx={{ borderRadius: '50px', borderColor: 'white', color: 'white' }}
                    >
                        Home Page
                    </Button>
                </Link>
            </motion.div>
        );
    };
    return (
        <>
            <Link href="/register">
                <Button
                    variant="contained"
                    size="large"
                    color="secondary"
                    endIcon={<ArrowForwardIcon />}
                    sx={{ borderRadius: '50px' }}
                >
                    Register
                </Button>
            </Link>
            <Link href="/login">
                <Button
                    variant="outlined"
                    size="large"
                    sx={{ borderRadius: '50px', borderColor: 'white', color: 'white' }}
                >
                    Login
                </Button>
            </Link>
        </>
    )
}
