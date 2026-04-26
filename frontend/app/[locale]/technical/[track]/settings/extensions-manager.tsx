'use client';

import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';

import { useTranslations } from 'next-intl';
import API from '@/app/utils/api.client';
import { useState } from 'react';
import { toast } from 'sonner';

interface Props {
    initialExtensions: string[];
}

export default function ExtensionsManager({ initialExtensions }: Props) {
    const [extensions, setExtensions] = useState<string[]>(initialExtensions);
    const [inputValue, setInputValue] = useState('');
    const [isSaving, setIsSaving] = useState(false);
    const tr = useTranslations('technicalSettingsPage');

    const handleAddExtension = (e: React.KeyboardEvent<HTMLInputElement> | React.MouseEvent) => {
        if ('key' in e && e.key !== 'Enter') return;
        e.preventDefault();

        let newExt = inputValue.trim().toLowerCase().replace(/\./g, '');
        if (!newExt) return;
        if (newExt === 'jpeg') newExt = 'jpg';

        if (extensions.includes(newExt)) {
            toast.warning(tr('extUsed', { newExt }));
        }

        setExtensions([...extensions, newExt]);
        setInputValue('');
    };

    const handleRemoveExtension = (extToRemove: string) => {
        setExtensions(extensions.filter(ext => ext !== extToRemove));
    };

    const handleSave = async () => {
        setIsSaving(true);
        toast.promise(async () => {
            const { response } = await API.PUT('/api/technical/extension/', {
                body: { extensions },
            });

            if (response.ok) {
                return await Promise.resolve();
            } else {
                return await Promise.reject();
            }
        },
            {
                loading: tr('saving'),
                success: tr('success'),
                error: tr('error'),
                finally() {
                    setIsSaving(false);
                },
            }
        );
    };

    return (
        <div className="w-full max-w-2xl mx-auto bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800 p-6 transition-colors duration-200">
            <div className="mb-6">
                <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100">{tr('allowedExts')}</h2>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    {tr('allowedExtsDesc')}
                </p>
            </div>

            <div className="flex flex-wrap gap-2 mb-6 min-h-12 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700/50">
                {extensions.length === 0 ? (
                    <span className="text-sm text-gray-400 dark:text-gray-500 italic flex items-center">{tr('noExts')}</span>
                ) : (
                    extensions.map((ext) => (
                        <Chip key={ext} color='primary' variant='outlined' label={`.${ext.toUpperCase()}`} onDelete={() => handleRemoveExtension(ext)} />
                    ))
                )}
            </div>

            <div className="flex gap-3 mb-6">
                <div className="relative flex-1">
                    <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-500 dark:text-gray-400 font-bold">
                        .
                    </span>
                    <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={handleAddExtension}
                        placeholder="e.g. png"
                        className="w-full pl-7 pr-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                    />
                </div>
                <Button onClick={handleAddExtension} variant='contained'>
                    {tr('add')}
                </Button>
            </div>

            <div className="flex justify-end pt-4 border-t border-gray-100 dark:border-gray-800">
                <Button
                    onClick={handleSave}
                    loading={isSaving}
                    variant='outlined'
                >
                    {isSaving ? tr('saving') : tr('save')}
                </Button>
            </div>
        </div>
    );
}