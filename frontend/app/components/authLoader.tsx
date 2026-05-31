"use client";

import React from 'react';
import dynamic from 'next/dynamic';
import API from '../utils/api.client';
import { usePathname } from '@/i18n/navigation';
import { serverGraphQL } from '../utils/gql_applolo';
import { GET_IMAGES_SETTINGS } from '../utils/graphql_helpers';
import { useAuthStore, useSettingsStore } from '../utils/store';
import type { SettingsImagesQuery } from '../generated/graphql';
import LoadingAnimation from './loading_animations/loading_animation';

interface AuthLoaderProps {
    children: React.ReactNode;
}

const DynamicSessionTimeoutDialog = dynamic(() => import('./session_timeout_dialog'));

export default function AuthLoader({ children }: AuthLoaderProps) {
    const path = usePathname();
    const isLoading = useAuthStore(state => state.isLoading);
    const setCredentials = useAuthStore(state => state.setCredentials);
    const logout = useAuthStore(state => state.logout);
    const setImages = useSettingsStore(state => state.setImages);

    React.useEffect(() => {
        let isMounted = true;

        const getData = async () => {
            const [authResponse, imagesResponse] = await Promise.allSettled([
                API.GET("/api/test-auth/"),
                serverGraphQL<SettingsImagesQuery>(GET_IMAGES_SETTINGS)
            ]);

            if (!isMounted) return;
    
            if (imagesResponse.status === "fulfilled" && imagesResponse.value.data.allSettings) {
                const { siteImage, heroImage } = imagesResponse.value.data.allSettings;
                setImages({
                    site_image: siteImage ? `${process.env.NEXT_PUBLIC_MEDIA_URL}${siteImage}` : '',
                    hero_image: heroImage ? `${process.env.NEXT_PUBLIC_MEDIA_URL}${heroImage}` : ''
                });
            }
    
            if (authResponse.status === "fulfilled" && authResponse.value.data) {
                const authData = authResponse.value.data;
                setCredentials({
                    isLoading: false,
                    isAuthed: true,
                    user: {
                        role: authData.role,
                        username: authData.username,
                        track: authData.track,
                        is_admin: authData.is_admin
                    }
                });
            } 
            else {
                logout();
                setCredentials({
                    isLoading: false,
                    isAuthed: false,
                    user: null
                });
            }
        }
        getData();
        return () => {
            isMounted = false;
        }
    }, [setCredentials, setImages, logout]);

    const isAuthed = useAuthStore(state => state.isAuthed);
    const isPublicRoute = path.includes("login") || path.includes("register") || path.includes("track-info/") || path === "/";

    if (isLoading) {
        return (
            <div className='flex w-full h-svh justify-center items-center'>
                <LoadingAnimation />
            </div>
        );
    }

    if (isAuthed || isPublicRoute) {
        return <>{children}</>;
    } else {
        return <DynamicSessionTimeoutDialog open />;
    }
}