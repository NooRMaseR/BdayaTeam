'use client';

import FormControlLabel from '@mui/material/FormControlLabel';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Switch from '@mui/material/Switch';

import type { components } from '@/app/generated/api_types';
import GroupTitled from '@/app/components/group_titled';
import FilePicker from '@/app/components/file_picker';
import { useAuthStore } from '@/app/utils/store';
import { useTranslations } from 'next-intl';
import BodyM from '@/app/components/bodyM';
import API from '@/app/utils/api.client';
import { toast } from 'sonner';
import React from 'react';

type Settings = components['schemas']['SettingsResponse'];
type OrganizerCanEditType = {
    key: Settings['organizer_can_edit'][0];
    label: string
};

type FormState = {
    settings: Settings;
    images: {
        site: { file: File | null; url: string | null };
        hero: { file: File | null; url: string | null };
    };
    isLoading: boolean;
};

type FormAction =
    | { type: 'UPDATE_SETTINGS'; payload: Settings }
    | { type: 'SET_SITE_IMAGE'; payload: { file: File | null; url: string | null } }
    | { type: 'SET_HERO_IMAGE'; payload: { file: File | null; url: string | null } }
    | { type: 'SET_LOADING'; payload: boolean };

function formReducer(state: FormState, action: FormAction): FormState {
    switch (action.type) {
        case 'UPDATE_SETTINGS':
            return { ...state, settings: action.payload };
        case 'SET_SITE_IMAGE':
            return { ...state, images: { ...state.images, site: action.payload } };
        case 'SET_HERO_IMAGE':
            return { ...state, images: { ...state.images, hero: action.payload } };
        case 'SET_LOADING':
            return { ...state, isLoading: action.payload };
        default:
            return state;
    }
}

export default function SettingsClient({ recivedSettings }: { recivedSettings: Settings }) {
    const tr = useTranslations('settingsPage');
    const isAdmin = useAuthStore(state => state.user?.is_admin);

    const initialFormState: FormState = {
        settings: recivedSettings,
        images: {
            site: { file: null, url: null },
            hero: { file: null, url: null },
        },
        isLoading: false,
    };

    const [state, dispatch] = React.useReducer(formReducer, initialFormState);

    React.useEffect(() => {
        return () => {
            if (state.images.site.url) URL.revokeObjectURL(state.images.site.url);
            if (state.images.hero.url) URL.revokeObjectURL(state.images.hero.url);
        };
    }, [state.images.site.url, state.images.hero.url]);

    const handleEditFieldsChange = (field: string, checked: boolean) => {
        const newSettings = {
            ...state.settings,
            organizer_can_edit: checked
                ? [...new Set([...state.settings.organizer_can_edit, field])] as OrganizerCanEditType['key'][]
                : state.settings.organizer_can_edit.filter(s => s !== field)
        };
        dispatch({ type: 'UPDATE_SETTINGS', payload: newSettings });
    }

    const handleRegisterToggle = (e: React.ChangeEvent<HTMLInputElement>) => {
        dispatch({ 
            type: 'UPDATE_SETTINGS', 
            payload: { ...state.settings, is_register_enabled: e.target.checked }
        });
    }

    const handleSiteImage = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            const url = URL.createObjectURL(file);
            dispatch({ type: 'SET_SITE_IMAGE', payload: { file, url } });
        }
    };

    const handleHeroImage = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            const url = URL.createObjectURL(file);
            dispatch({ type: 'SET_HERO_IMAGE', payload: { file, url } });
        }
    };

    const saveSettings = () => {
        dispatch({ type: 'SET_LOADING', payload: true });

        const submissionPromise = API.PUT("/api/organizer/settings/", {
            body: {
                is_register_enabled: state.settings.is_register_enabled,
                organizer_can_edit: state.settings.organizer_can_edit,
                site_image: state.images.site.file as unknown as string,
                hero_image: state.images.hero.file as unknown as string
            },
            bodySerializer(body) {
                const fd = new FormData();
                if (isAdmin) fd.append("is_register_enabled", String(body.is_register_enabled));

                body.organizer_can_edit?.forEach(v => v.trim() != '' && fd.append("organizer_can_edit", v));

                if (state.images.site.file) fd.append("site_image", state.images.site.file);
                if (state.images.hero.file) fd.append("hero_image", state.images.hero.file);

                return fd;
            }
        }).then(({ response, error }) => {
            if (!response.ok) throw error;
            return response;
        });

        toast.promise(submissionPromise, {
            loading: tr('saving'),
            success: tr('saved'),
            error: tr('notSaved'),
            finally: () => dispatch({ type: 'SET_LOADING', payload: false })
        });
    };

    const editableFields: OrganizerCanEditType[] = [
        { key: "name", label: tr('name') },
        { key: 'status', label: tr('status') },
        { key: 'track', label: tr('track') },
        { key: 'bonus', label: tr('bonus') },
        { key: 'email', label: tr('email') },
        { key: 'phone', label: tr('phone') },
    ];

    return (
        <BodyM>
            <div className="max-w-4xl mx-auto py-8 px-4 flex flex-col gap-8">

                <div>
                    <Typography variant="h4" fontWeight="bold" gutterBottom>
                        {tr('settings')}
                    </Typography>
                    <Typography color="text.secondary">
                        {tr('settingsDesc')}
                    </Typography>
                </div>

                {
                    isAdmin &&
                    <GroupTitled title={tr('access')}>
                        <FormControlLabel
                            control={<Switch color="primary" checked={!!state.settings.is_register_enabled} onChange={handleRegisterToggle} />}
                            label={<Typography fontWeight="medium">{tr('memberCan')}</Typography>}
                        />
                    </GroupTitled>
                }

                <GroupTitled title={tr('orgEdit')} caption={tr('orgEditDesc')} >
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-y-2 gap-x-6">
                        {editableFields.map(field => (
                            <FormControlLabel
                                key={field.key}
                                control={
                                    <Switch
                                        color="secondary"
                                        checked={state.settings.organizer_can_edit?.includes(field.key) || false}
                                        onChange={(e) => handleEditFieldsChange(field.key, e.target.checked)}
                                    />
                                }
                                label={field.label}
                            />
                        ))}
                    </div>
                </GroupTitled>

                <GroupTitled title={tr('branding')} >
                    <div className="flex flex-col md:flex-row gap-8">
                        <div className="flex-1 flex flex-col gap-2">
                            <Typography variant="subtitle2" fontWeight="bold">{tr('logo')}</Typography>
                            <FilePicker
                                accept='image/png,image/jpg,image/jpeg,image/ico,image/webp'
                                onChange={handleSiteImage}
                                preview={state.images.site.url || state.settings.site_image}
                            />
                        </div>
                        <div className="flex-1 flex flex-col gap-2">
                            <Typography variant="subtitle2" fontWeight="bold">{tr('hero')}</Typography>
                            <FilePicker
                                accept='image/png,image/jpg,image/jpeg,image/webp'
                                onChange={handleHeroImage}
                                preview={state.images.hero.url || state.settings.hero_image}
                            />
                        </div>
                    </div>
                </GroupTitled>

                <div className="flex justify-end pt-4 pb-12">
                    <Button
                        onClick={saveSettings}
                        disabled={state.isLoading}
                        variant='contained'
                        size="large"
                        sx={{ px: 6, py: 1.5, borderRadius: 2, fontWeight: 'bold' }}
                    >
                        {state.isLoading ? tr('saving') : tr('save')}
                    </Button>
                </div>

            </div>
        </BodyM>
    )
}