import type { components } from '../generated/api_types';
import { create } from "zustand";

export type UserAuth = {
    isLoading: boolean;
    isAuthed: boolean;
    user: components['schemas']['LoginResponse'] | null;
}
type SettingsImages = components['schemas']['SettingsImagesResponse'];

interface UserAuthStoreType extends UserAuth {
    setCredentials: (payload: UserAuth) => void;
    logout: () => void;
}

interface SettingsImagesStoreType extends SettingsImages {
    setSiteImage: (url: SettingsImages['site_image']) => void;
    setHeroImage: (url: SettingsImages['hero_image']) => void;
    setImages: (images: SettingsImages) => void;
}

export const useAuthStore = create<UserAuthStoreType>((set) => ({
    isLoading: true,
    isAuthed: false,
    user: null,
    setCredentials: (payload: UserAuth) => set(payload),
    logout: () => set({ user: null, isAuthed: false, isLoading: false })
}))

export const useSettingsStore = create<SettingsImagesStoreType>((set) => ({
    hero_image: null,
    site_image: null,
    setSiteImage: (url: SettingsImages['site_image']) => set({ site_image: url }),
    setHeroImage: (url: SettingsImages['hero_image']) => set({ hero_image: url }),
    setImages: (images: SettingsImages) => set(images)
}))

