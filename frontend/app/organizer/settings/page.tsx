'use client';

import { Button, CircularProgress, FormControlLabel, Switch } from '@mui/material';
import type { GetAllSettingsQuery } from '@/app/generated/graphql';
import { GET_ALL_SETTINGS } from '@/app/utils/graphql_helpers';
import type { components } from '@/app/generated/api_types';
import { serverGraphQL } from '@/app/utils/api_utils';
import FilePicker from '@/app/components/file_picker';
import { API } from '@/app/utils/api.client';
import { toast } from 'sonner';
import React from 'react';

type Settings = components['schemas']['SiteSettingsRequest'];

export default function SettingsPage() {
    const [settings, setSettings] = React.useState<Settings>({ is_register_enabled: false, organizer_can_edit: [], site_image: '', hero_image: '' });
    const [siteImage, setSiteImage] = React.useState<File | null>(null);
    const [heroImage, setHeroImage] = React.useState<File | null>(null);
    const [isLoading, setIsLoading] = React.useState<boolean>(true);

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
                loading: "Saving.....",
                success: "Saved Successfully",
                error: "Couldn't Save"
            }
        );
    }

    React.useEffect(() => {
        const req = async () => {
            const res = await serverGraphQL<GetAllSettingsQuery>(GET_ALL_SETTINGS);
            const setting = res.data.allSettings;
            if (setting) {
                setSettings({
                    is_register_enabled: setting.isRegisterEnabled,
                    organizer_can_edit: setting.organizerCanEdit,
                    site_image: setting.siteImage || '',
                    hero_image: setting.heroImage || '',
                });
            }
            setIsLoading(false);
        };
        req();
    }, []);

    if (isLoading) {
        return <div className='w-full h-[86svh] flex justify-center items-center'>
            <CircularProgress />
        </div>
    }

    return (
        <div className="w-full h-[85svh] flex flex-col p-4">
            <FormControlLabel control={<Switch checked={settings.is_register_enabled} onChange={handleRegister} />} label="Member Can Register" sx={{ width: "fit-content" }} />
            <hr />
            <FormControlLabel control={<Switch checked={settings.organizer_can_edit?.includes("code")} onChange={(e) => handleEditFieldsChange("code", e.target.checked)} />} label={"code"} sx={{ width: "fit-content" }} />
            <FormControlLabel control={<Switch checked={settings.organizer_can_edit?.includes("name")} onChange={(e) => handleEditFieldsChange("name", e.target.checked)} />} label={"name"} sx={{ width: "fit-content" }} />
            <FormControlLabel control={<Switch checked={settings.organizer_can_edit?.includes("status")} onChange={(e) => handleEditFieldsChange("status", e.target.checked)} />} label={"status"} sx={{ width: "fit-content" }} />
            <FormControlLabel control={<Switch checked={settings.organizer_can_edit?.includes("track")} onChange={(e) => handleEditFieldsChange("track", e.target.checked)} />} label={"track"} sx={{ width: "fit-content" }} />
            <FormControlLabel control={<Switch checked={settings.organizer_can_edit?.includes("bonus")} onChange={(e) => handleEditFieldsChange("bonus", e.target.checked)} />} label={"bonus"} sx={{ width: "fit-content" }} />
            <FormControlLabel control={<Switch checked={settings.organizer_can_edit?.includes("email")} onChange={(e) => handleEditFieldsChange("email", e.target.checked)} />} label={"email"} sx={{ width: "fit-content" }} />
            <FormControlLabel control={<Switch checked={settings.organizer_can_edit?.includes("phone")} onChange={(e) => handleEditFieldsChange("phone", e.target.checked)} />} label={"phone"} sx={{ width: "fit-content" }} />
            <hr />
            <FilePicker accept='image/png,image/jpg,image/jpeg,image/ico,image/webp' onChange={handleSiteImage} preview={settings.site_image || siteImage as unknown as string} />
            <FilePicker accept='image/png,image/jpg,image/jpeg,image/ico,image/webp' onChange={handleHeroImage} preview={settings.hero_image || heroImage as unknown as string} />
            <Button onClick={saveSettings} variant='contained'>Save</Button>
        </div>
    )
}
