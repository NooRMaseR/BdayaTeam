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

export default function SettingsClient({ recivedSettings }: { recivedSettings: Settings }) {
    const tr = useTranslations('settingsPage');
    const isAdmin = useAuthStore(state => state.user?.is_admin);
    const [settings, setSettings] = React.useState<Settings>(recivedSettings);
    
    const [siteImageFile, setSiteImageFile] = React.useState<File | null>(null);
    const [heroImageFile, setHeroImageFile] = React.useState<File | null>(null);
    
    const [siteImageUrl, setSiteImageUrl] = React.useState<string | null>(null);
    const [heroImageUrl, setHeroImageUrl] = React.useState<string | null>(null);
    
    const [isLoading, setIsLoading] = React.useState<boolean>(false);

    React.useEffect(() => {
        return () => {
            if (siteImageUrl) URL.revokeObjectURL(siteImageUrl);
            if (heroImageUrl) URL.revokeObjectURL(heroImageUrl);
        };
    }, [siteImageUrl, heroImageUrl]);

    const handleEditFieldsChange = (field: string, checked: boolean) => {
        setSettings(prev => {
            return {
                ...prev,
                organizer_can_edit: checked 
                    ? [...new Set([...prev.organizer_can_edit, field])] as OrganizerCanEditType['key'][]
                    : prev.organizer_can_edit.filter(s => s !== field)
            };
        });
    }

    const handleRegisterToggle = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSettings(prev => ({ ...prev, is_register_enabled: e.target.checked }));
    }

    const handleSiteImage = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            setSiteImageFile(file);
            const url = URL.createObjectURL(file);
            setSiteImageUrl(url);
        }
    };

    const handleHeroImage = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            setHeroImageFile(file);
            const url = URL.createObjectURL(file);
            setHeroImageUrl(url);
        }
    };

    const saveSettings = () => {
        setIsLoading(true);
        
        const submissionPromise = API.PUT("/api/organizer/settings/", {
            body: {
                is_register_enabled: settings.is_register_enabled,
                organizer_can_edit: settings.organizer_can_edit,
                site_image: siteImageFile as unknown as string,
                hero_image: heroImageFile as unknown as string
            },
            bodySerializer(body) {
                const fd = new FormData();
                if (isAdmin) fd.append("is_register_enabled", String(body.is_register_enabled));
                
                body.organizer_can_edit?.forEach(v => v.trim() != '' && fd.append("organizer_can_edit", v));
                
                if (siteImageFile) fd.append("site_image", siteImageFile);
                if (heroImageFile) fd.append("hero_image", heroImageFile);
                
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
            finally: () => setIsLoading(false)
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
                                control={<Switch color="primary" checked={!!settings.is_register_enabled} onChange={handleRegisterToggle} />} 
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
                                        checked={settings.organizer_can_edit?.includes(field.key) || false} 
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
                                preview={siteImageUrl || settings.site_image} 
                            />
                        </div>
                        <div className="flex-1 flex flex-col gap-2">
                            <Typography variant="subtitle2" fontWeight="bold">{tr('hero')}</Typography>
                            <FilePicker 
                                accept='image/png,image/jpg,image/jpeg,image/webp' 
                                onChange={handleHeroImage} 
                                preview={heroImageUrl || settings.hero_image} 
                            />
                        </div>
                    </div>
                </GroupTitled>

                <div className="flex justify-end pt-4 pb-12">
                    <Button 
                        onClick={saveSettings} 
                        disabled={isLoading} 
                        variant='contained' 
                        size="large"
                        sx={{ px: 6, py: 1.5, borderRadius: 2, fontWeight: 'bold' }}
                    >
                        {isLoading ? tr('saving') : tr('save')}
                    </Button>
                </div>

            </div>
        </BodyM>
    )
}