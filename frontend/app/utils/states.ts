import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type { components } from '../generated/api_types';

export type UserAuth = {
    isLoading: boolean;
    isAuthed: boolean;
    user: components['schemas']['Login'] | null;
}

export type SettingsImages = components['schemas']['SiteSettingsImages'];

const initialAuthState: UserAuth = {
    isLoading: true,
    isAuthed: false,
    user: null
} 

const authSlice = createSlice({
    name: "auth",
    initialState: initialAuthState,
    reducers: {
        setCredentials: (state, action: PayloadAction<UserAuth>) => {
            state.isLoading = action.payload.isLoading;
            state.isAuthed = action.payload.isAuthed;
            state.user = action.payload.user;
        },
        logout: (state) => {
            state.isLoading = false;
            state.isAuthed = false;
            state.user = null;
        }
    }
});

const settingsSlice = createSlice({
    name: "settings",
    initialState: {
        site_image: null,
        hero_image: null,
    } as SettingsImages,
    reducers: {
        setSiteImage: (state, action: PayloadAction<SettingsImages['site_image']>) => {
            state.site_image = action.payload;
        },
        setHeroImage: (state, action: PayloadAction<SettingsImages['hero_image']>) => {
            state.hero_image = action.payload;
        },
        setAllImage: (state, action: PayloadAction<SettingsImages>) => {
            state.hero_image = action.payload.hero_image;
            state.site_image = action.payload.site_image;
        },
    }
})

export const { setCredentials, logout } = authSlice.actions;
export const { setSiteImage, setHeroImage, setAllImage } = settingsSlice.actions;
export const authReducer = authSlice.reducer;
export const settingsReducer = settingsSlice.reducer;

