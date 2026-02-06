"use client";

import React from 'react';
import { API } from '../utils/api.client';
import { usePathname } from 'next/navigation';
import { serverGraphQL } from '../utils/api_utils';
import SessionTimeoutDialog from './session_timeout_dialog';
import { GET_IMAGES_SETTINGS } from '../utils/graphql_helpers';
import { useAppDispatch, useAppSelector } from '../utils/hooks';
import type { SettingsImagesQuery } from '../generated/graphql';
import { logout, setAllImage, setCredentials } from '../utils/states';
import LoadingAnimation from './loading_animations/loading_animation';

export default function AuthLoader({ children }: { children: React.ReactNode }) {
    const dispatch = useAppDispatch();
    const path = usePathname()
    const isAuthed = useAppSelector(state => state.auth.isAuthed);
    const [isLoading, setIsLoading] = React.useState<boolean>(true);

    React.useEffect(() => {
        const req = async () => {
            const [authResponse, images] = await Promise.allSettled(
                [
                    API.GET("/api/test-auth/"),
                    serverGraphQL<SettingsImagesQuery>(GET_IMAGES_SETTINGS)
                ]
            );

            if (images.status === "fulfilled") {
                if (images.value.data.allSettings) {
                    const { siteImage, heroImage } = images.value.data.allSettings;
                    dispatch(setAllImage({
                        site_image: siteImage ? `${process.env.NEXT_PUBLIC_MEDIA_URL}${siteImage}` : undefined,
                        hero_image: heroImage ? `${process.env.NEXT_PUBLIC_MEDIA_URL}${heroImage}` : undefined
                    }));
                };
            }


            if (authResponse.status === 'fulfilled' && authResponse.value.data) {
                dispatch(setCredentials({
                    isLoading: false,
                    isAuthed: true,
                    user: {
                        role: authResponse.value.data.role,
                        username: authResponse.value.data.username,
                        track: authResponse.value.data.track
                    }
                }));
                setIsLoading(false);
            } else {
                dispatch(logout());
                setIsLoading(false);
            }
        };
        req();
    }, [dispatch]);

    if (isLoading) {
        return (
            <div className='flex w-full h-svh justify-center items-center'>
                <LoadingAnimation />
            </div>
        );
    };

    if (isAuthed || path.includes("login") || path.includes("register") || path.includes("/")) {
        return children;
    } else {
        return (
            <SessionTimeoutDialog open />
        )
    }
    
}
