"use client";

import React from 'react'
import { API } from '../utils/api.client';
import { useDispatch } from 'react-redux';
import { useAppSelector } from '../utils/hooks';
import { CircularProgress } from '@mui/material';
import { logout, setCredentials} from '../utils/states';

export default function AuthLoader({ children }: { children: React.ReactNode }) {
    const dispatch = useDispatch();
    const isLoading = useAppSelector((state) => state.auth.isLoading);

    React.useEffect(() => {
        const req = async () => {
            const {data, response} = await API.GET("/test-auth/");

            if (response.ok && data) {
                dispatch(setCredentials({ isLoading: false, isAuthed: true, user: data}));
            } else {
                dispatch(logout());
            }
        };
        req();
    }, [dispatch]);
    
    if (isLoading) {
        return (
            <div className='flex w-full h-svh justify-center items-center'>
                <CircularProgress />
            </div>
        );
    };
    return children;
}
