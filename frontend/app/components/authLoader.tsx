"use client";

import React from 'react';
import API from '../utils/api.client';
import type { components } from '../generated/api_types';
import { usePathname, useRouter } from '@/i18n/navigation';
import SessionTimeoutDialog from './session_timeout_dialog';
import { useAuthStore, useSettingsStore } from '../utils/store';
import type { SettingsImagesQuery } from '../generated/graphql';
import LoadingAnimation from './loading_animations/loading_animation';

interface AuthLoaderProps {
    authData: components["schemas"]["TestAuthResponse"] | null;
    imagesData: SettingsImagesQuery['allSettings'];
    children: React.ReactNode;
}

export default function AuthLoader({ authData, imagesData, children }: AuthLoaderProps) {
    const path = usePathname();
    const router = useRouter();
    const setCredentials = useAuthStore(state => state.setCredentials);
    const logout = useAuthStore(state => state.logout);
    const setImages = useSettingsStore(state => state.setImages);
    
    // Track if we are actively fixing the cookies in the browser
    const [isRefreshingClient, setIsRefreshingClient] = React.useState(false);

    React.useEffect(() => {
        if (imagesData) {
            const { siteImage, heroImage } = imagesData;
            setImages({
                site_image: siteImage ? `${process.env.NEXT_PUBLIC_MEDIA_URL}${siteImage}` : null,
                hero_image: heroImage ? `${process.env.NEXT_PUBLIC_MEDIA_URL}${heroImage}` : null
            });
        }

        // 1. If the Server succeeded, sync to Zustand!
        if (authData) {
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
        // 2. The Server failed. Time for the Browser to fix the cookies!
        else {
            const runClientFallback = async () => {
                setIsRefreshingClient(true);
                
                // This request triggers your api.client.ts interceptor.
                // The interceptor will fetch the new HttpOnly cookies and the browser will save them!
                const res = await API.GET("/api/test-auth/");
                
                if (res.data) {
                    setCredentials({
                        isLoading: false,
                        isAuthed: true,
                        user: { ...res.data }
                    });
                    // Tell Next.js to re-run the Server Components now that the browser has the new cookies!
                    router.refresh(); 
                } else {
                    // The refresh token is completely dead. Log out.
                    logout();
                }
                setIsRefreshingClient(false);
            };
            
            runClientFallback();
        }
    }, [authData, imagesData, setCredentials, setImages, logout, router]);

    const isAuthed = useAuthStore(state => state.isAuthed);
    const isPublicRoute = path.includes("login") || path.includes("register") || path.includes("track-info/") || path === "/";

    if (isRefreshingClient) {
        return (
            <div className='flex w-full h-svh justify-center items-center'>
                <LoadingAnimation />
            </div>
        );
    }

    if (isAuthed || isPublicRoute) {
        return <>{children}</>;
    } else {
        return <SessionTimeoutDialog open />;
    }
}