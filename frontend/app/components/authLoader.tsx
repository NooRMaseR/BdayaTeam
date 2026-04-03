"use client";

import React from 'react';
import API from '../utils/api.client';
import { usePathname } from '@/i18n/navigation';
import { serverGraphQL } from '../utils/api_utils';
import SessionTimeoutDialog from './session_timeout_dialog';
import { GET_IMAGES_SETTINGS } from '../utils/graphql_helpers';
import type { SettingsImagesQuery } from '../generated/graphql';
import { useAuthStore, useSettingsStore } from '../utils/store';
import LoadingAnimation from './loading_animations/loading_animation';

export default function AuthLoader({ children }: { children: React.ReactNode }) {
    const path = usePathname()
    const isAuthed = useAuthStore(state => state.isAuthed);
    const setCredentials = useAuthStore(state => state.setCredentials);
    const logout = useAuthStore(state => state.logout);
    const setImages = useSettingsStore(state => state.setImages);
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
                    setImages({
                        site_image: siteImage ? `${process.env.NEXT_PUBLIC_MEDIA_URL}${siteImage}` : null,
                        hero_image: heroImage ? `${process.env.NEXT_PUBLIC_MEDIA_URL}${heroImage}` : null
                    });
                };
            }


            if (authResponse.status === 'fulfilled' && authResponse.value.data) {
                setCredentials({
                    isLoading: false,
                    isAuthed: true,
                    user: {
                        role: authResponse.value.data.role,
                        username: authResponse.value.data.username,
                        track: authResponse.value.data.track,
                        is_admin: authResponse.value.data.is_admin
                    }
                });
                setIsLoading(false);
            } else {
                logout();
                setIsLoading(false);
            }
        };
        req();
    }, [logout, setCredentials, setImages]);

    if (isLoading) {
        return (
            <div className='flex w-full h-svh justify-center items-center'>
                <LoadingAnimation />
            </div>
        );
    };

    if (isAuthed || path.includes("login") || path.includes("register") || path.includes("track-info/") || path === "/") {
        return children;
    } else {
        return (
            <SessionTimeoutDialog open />
        )
    }
    
}
