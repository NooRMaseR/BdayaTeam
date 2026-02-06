'use client';

import FormControlLabel from '@mui/material/FormControlLabel';
import Button from '@mui/material/Button';
import Switch from '@mui/material/Switch';

import type { components } from '@/app/generated/api_types';
import FilePicker from '@/app/components/file_picker';
import { API } from '@/app/utils/api.client';
import { useTranslations } from 'next-intl';
import BodyM from '@/app/components/bodyM';
import { toast } from 'sonner';
import React from 'react';

type Settings = components['schemas']['SiteSettingsRequest'];

export default function SettingsClient({recivedSettings}: {recivedSettings: Settings}) {
    const [settings, setSettings] = React.useState<Settings>(recivedSettings);
    const [siteImage, setSiteImage] = React.useState<File | null>(null);
    const [heroImage, setHeroImage] = React.useState<File | null>(null);
    const [isLoading, setIsLoading] = React.useState<boolean>(false);
    const tr = useTranslations('settingsPage');

    const handleEditFieldsChange = (field: string, checked: boolean) => {
        const data: Settings = {
            is_register_enabled: settings.is_register_enabled,
            site_image: settings.site_image,
            hero_image: settings.hero_image,
            organizer_can_edit: []
        }
        if (checked) {
            data.organizer_can_edit = settings.organizer_can_edit?.find((s) => s === field) ? settings.organizer_can_edit : [...(settings.organizer_can_edit || []), field];
        } else {
            data.organizer_can_edit = settings.organizer_can_edit?.filter((s) => s !== field);
        };
        setSettings(data);
    }

    const handleRegister = (e: React.ChangeEvent<HTMLInputElement>) => {
        console.info(e.target.checked);
        setSettings({
            is_register_enabled: e.target.checked,
            site_image: settings.site_image,
            hero_image: settings.hero_image,
            organizer_can_edit: settings.organizer_can_edit,
        });
    }

    const handelImage = (e: React.ChangeEvent<HTMLInputElement>, func: React.Dispatch<React.SetStateAction<File | null>>, varName: string) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            func(file);
            const d: Record<string, string> = {};
            
            const obj = URL.createObjectURL(file);
            d[varName] = obj;
            setSettings(pre => ({ ...pre, ...d }));
            return () => URL.revokeObjectURL(obj);
        }
    };

    const handleSiteImage = (e: React.ChangeEvent<HTMLInputElement>) => handelImage(e, setSiteImage, "siteImage");
    const handleHeroImage = (e: React.ChangeEvent<HTMLInputElement>) => handelImage(e, setHeroImage, "heroImage");

    const saveSettings = () => {
        setIsLoading(true);
        const dataSettings = {
            ...settings,
            siteImage: siteImage,
            heroImage: heroImage
        }
        toast.promise(async () => {
            const formdata = new FormData();
            formdata.append("is_register_enabled", String(dataSettings.is_register_enabled));
            dataSettings.organizer_can_edit?.forEach(v => formdata.append("organizer_can_edit", v));
            
            if (dataSettings.siteImage)
                formdata.append("site_image", dataSettings.siteImage);
            
            if (dataSettings.heroImage)
                formdata.append("hero_image", dataSettings.heroImage as Blob);

            const { response } = await API.PUT(
                "/api/organizer/settings/", {
                body: formdata as unknown as {
                    is_register_enabled?: boolean | undefined;
                    organizer_can_edit?: string[] | undefined;
                    site_image?: string | null | undefined;
                },
            });

            if (response.ok) {
                return await Promise.resolve();
            };
            return await Promise.reject();
        },
            {
                loading: tr('saving'),
                success: tr('saved'),
                error: tr('notSaved'),
                finally() { setIsLoading(false); }
            }
        );
    };

    return (
        <BodyM>
            <div className="w-full h-[85svh] flex flex-col p-4">
                <FormControlLabel control={<Switch checked={settings.is_register_enabled} onChange={handleRegister} />} label={tr('memberCan')} sx={{ width: "fit-content" }} />
                <hr />
                <FormControlLabel control={<Switch checked={settings.organizer_can_edit?.includes("code")} onChange={(e) => handleEditFieldsChange("code", e.target.checked)} />} label={tr("code")} sx={{ width: "fit-content" }} />
                <FormControlLabel control={<Switch checked={settings.organizer_can_edit?.includes("name")} onChange={(e) => handleEditFieldsChange("name", e.target.checked)} />} label={tr("name")} sx={{ width: "fit-content" }} />
                <FormControlLabel control={<Switch checked={settings.organizer_can_edit?.includes("status")} onChange={(e) => handleEditFieldsChange("status", e.target.checked)} />} label={tr("status")} sx={{ width: "fit-content" }} />
                <FormControlLabel control={<Switch checked={settings.organizer_can_edit?.includes("track")} onChange={(e) => handleEditFieldsChange("track", e.target.checked)} />} label={tr("track")} sx={{ width: "fit-content" }} />
                <FormControlLabel control={<Switch checked={settings.organizer_can_edit?.includes("bonus")} onChange={(e) => handleEditFieldsChange("bonus", e.target.checked)} />} label={tr("bonus")} sx={{ width: "fit-content" }} />
                <FormControlLabel control={<Switch checked={settings.organizer_can_edit?.includes("email")} onChange={(e) => handleEditFieldsChange("email", e.target.checked)} />} label={tr("email")} sx={{ width: "fit-content" }} />
                <FormControlLabel control={<Switch checked={settings.organizer_can_edit?.includes("phone")} onChange={(e) => handleEditFieldsChange("phone", e.target.checked)} />} label={tr("phone")} sx={{ width: "fit-content" }} />
                <hr />
                <FilePicker accept='image/png,image/jpg,image/jpeg,image/ico,image/webp' onChange={handleSiteImage} preview={settings.site_image || siteImage as unknown as string} />
                <FilePicker accept='image/png,image/jpg,image/jpeg,image/ico,image/webp' onChange={handleHeroImage} preview={settings.hero_image || heroImage as unknown as string} />
                <Button onClick={saveSettings} loading={isLoading} loadingPosition='start' variant='contained'>{tr('save')}</Button>
            </div>
        </BodyM>
    )
}
