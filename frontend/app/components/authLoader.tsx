"use client";

import React from 'react'
import { API } from '../utils/api.client';
import { useDispatch } from 'react-redux';
import { useAppSelector } from '../utils/hooks';
import { CircularProgress } from '@mui/material';
import { serverGraphQL } from '../utils/api_utils';
import { GET_IMAGES_SETTINGS } from '../utils/graphql_helpers';
import type { SettingsImagesQuery } from '../generated/graphql';
import { logout, setAllImage, setCredentials} from '../utils/states';

export default function AuthLoader({ children }: { children: React.ReactNode }) {
    const dispatch = useDispatch();
    const isLoading = useAppSelector((state) => state.auth.isLoading);

    React.useEffect(() => {
        const req = async () => {
            const [ test, images ] = await Promise.allSettled(
                [
                    API.GET("/api/test-auth/"),
                    serverGraphQL<SettingsImagesQuery>(GET_IMAGES_SETTINGS)
                ]
            );
            if (images.status === "fulfilled") {
                const siteImage = images.value.data.allSettings?.siteImage;
                const heroImage = images.value.data.allSettings?.heroImage;
                dispatch(setAllImage({
                    site_image: siteImage ? `${process.env.NEXT_PUBLIC_MEDIA_URL}${siteImage}` : undefined,
                    hero_image: heroImage ? `${process.env.NEXT_PUBLIC_MEDIA_URL}${heroImage}` : undefined
                }));
            }
            if (test.status === "fulfilled" && test.value.data) {
                dispatch(setCredentials({ isLoading: false, isAuthed: true, user: { role: test.value.data.role, username: test.value.data.username, track: test.value.data.track } }));
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
