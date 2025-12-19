"use client";

import React from 'react';
import serverApi from '../utils/api';
import { useDispatch } from 'react-redux';
import { GetLogIn } from '../utils/api_types_helper';
import { logout, setCredentials } from '../utils/states';

export default function AuthLoader({ children }: { children: React.ReactNode }) {
    const dispatch = useDispatch();

    React.useEffect(() => {
        const req = async () => {
            const res = await serverApi<GetLogIn>("GET", "/test-auth/");
            if (res.success && res.data) {
                dispatch(setCredentials({ isLoading: false, isAuthed: true, user: res.data }));
            } else {
                dispatch(logout());
            }
        }
        req();
    }, [dispatch]);

    return children;
}
