'use client';

import { GetAllSettingsQuery, UpdateSettingsMutation } from '@/app/generated/graphql';
import { Button, CircularProgress, FormControlLabel, Switch } from '@mui/material';
import type { Settings } from '@/app/utils/api_types_helper';
import { serverGraphQL } from '@/app/utils/api_utils';
import { gql } from 'graphql-tag';
import { print } from "graphql";
import { toast } from 'sonner';
import React from 'react';

const UPDATE_SETTINGS = gql`
    mutation UpdateSettings($isRegisterEnabled: Boolean, $organizerCanEdit: [String]) {
        updateSettings(isRegisterEnabled: $isRegisterEnabled, organizerCanEdit: $organizerCanEdit) {
            success
        }
    }
`;

const GET_ALL_SETTINGS = gql`
    query GetAllSettings{
        allSettings {
            siteImage
            isRegisterEnabled
            organizerCanEdit
        }
    }
`;

export default function SettingsPage() {
    const [settings, setSettings] = React.useState<Settings>({ isRegisterEnabled: false, organizerCanEdit: [], siteImage: '' });
    const [isLoading, setIsLoading] = React.useState<boolean>(true);

    const handelEditFieldsChange = (field: string, checked: boolean) => {
        const data: Settings = {
            isRegisterEnabled: settings.isRegisterEnabled,
            siteImage: settings.siteImage,
            organizerCanEdit: []
        }
        if (checked) {
            data.organizerCanEdit = settings.organizerCanEdit.find((s) => s === field) ? settings.organizerCanEdit : [...settings.organizerCanEdit, field];
        } else {
            data.organizerCanEdit = settings.organizerCanEdit.filter((s) => s !== field);
        };
        setSettings(data);
    }

    const handelRegister = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSettings({
            isRegisterEnabled: e.target.checked,
            siteImage: settings.siteImage,
            organizerCanEdit: settings.organizerCanEdit
        });
    }

    const saveSettings = () => {
        toast.promise(async () => {
            const res = await serverGraphQL<UpdateSettingsMutation>(
                print(UPDATE_SETTINGS),
                settings,
                true
            );
            
            if (res.updateSettings?.success) {
                return await Promise.resolve();
            }
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
            const res = await serverGraphQL<GetAllSettingsQuery>(
                print(GET_ALL_SETTINGS)
            );
            const setting = res.allSettings;
            if (setting) {
                setSettings({
                    isRegisterEnabled: setting.isRegisterEnabled,
                    organizerCanEdit: setting.organizerCanEdit,
                    siteImage: setting.siteImage || settings.siteImage
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
            <FormControlLabel control={<Switch checked={settings.isRegisterEnabled} onChange={handelRegister} />} label="Member Can Register" />
            <hr />
            <FormControlLabel control={<Switch checked={settings.organizerCanEdit.includes("code")} onChange={(e) => handelEditFieldsChange("code", e.target.checked)} />} label={"code"} />
            <FormControlLabel control={<Switch checked={settings.organizerCanEdit.includes("name")} onChange={(e) => handelEditFieldsChange("name", e.target.checked)} />} label={"name"} />
            <FormControlLabel control={<Switch checked={settings.organizerCanEdit.includes("status")} onChange={(e) => handelEditFieldsChange("status", e.target.checked)} />} label={"status"} />
            <FormControlLabel control={<Switch checked={settings.organizerCanEdit.includes("track")} onChange={(e) => handelEditFieldsChange("track", e.target.checked)} />} label={"track"} />
            <FormControlLabel control={<Switch checked={settings.organizerCanEdit.includes("bonus")} onChange={(e) => handelEditFieldsChange("bonus", e.target.checked)} />} label={"bonus"} />
            <FormControlLabel control={<Switch checked={settings.organizerCanEdit.includes("email")} onChange={(e) => handelEditFieldsChange("email", e.target.checked)} />} label={"email"} />
            <FormControlLabel control={<Switch checked={settings.organizerCanEdit.includes("phone")} onChange={(e) => handelEditFieldsChange("phone", e.target.checked)} />} label={"phone"} />
            <hr />
            <input type='image' />
            <Button onClick={saveSettings} variant='contained'>Save</Button>
        </div>
    )
}
