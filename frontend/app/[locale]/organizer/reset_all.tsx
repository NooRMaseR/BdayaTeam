'use client';

import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import NavigationCard from '../../components/navigation_card';
import DialogContentText from '@mui/material/DialogContentText';

import { useAuthStore } from '@/app/utils/store';
import { useRouter } from '@/i18n/navigation';
import { useTranslations } from 'next-intl';
import API from '../../utils/api.client';
import { toast } from 'sonner';
import React from 'react';

type ResetDialogProps = {
    open: boolean;
    isLoading: boolean;
    onCancel: () => void;
    onReset: () => void;
}

function ResetDialog({ open, isLoading, onCancel, onReset }: ResetDialogProps) {
    const tr = useTranslations('organizerPage');

    return (
        <Dialog open={open}>
            <DialogTitle>{tr('resetTitle')}?</DialogTitle>
            <DialogContent>
                <DialogContentText>
                    {tr('resetConf')}
                </DialogContentText>
                <DialogContentText color='error'>
                    {tr('resetText')}
                </DialogContentText>
            </DialogContent>
            <DialogActions>
                <Button variant='contained' onClick={onCancel} loading={isLoading}>{tr('cancel')}</Button>
                <Button variant='outlined' color='error' onClick={onReset} loading={isLoading}>{tr('reset')}</Button>
            </DialogActions>
        </Dialog>
    )
}

export default function ResetAll() {
    const [open, setOpen] = React.useState<boolean>(false);
    const [isLoading, setIsLoading] = React.useState<boolean>(false);
    const navigation = useRouter();
    const isSuperUser = useAuthStore(state => state.user?.is_admin);
    const tr = useTranslations('organizerPage');

    const openDialog = () => setOpen(true);
    const closeDialog = () => setOpen(false);
    const handleReset = () => {
        setIsLoading(true);
        toast.promise(async () => {
            const { response } = await API.DELETE('/api/reset-all/');
            if (response.ok) {
                return await Promise.resolve();
            }
            return await Promise.reject(response.status);
        }, {
            loading: tr('reseting'),
            success() {
                closeDialog();
                navigation.refresh();
                return tr("resetSuccess");
            },
            error(code) {
                if (code === 403) {
                    return tr('noPerm');
                }
                return tr('wrong');
            },
            finally() {
                setIsLoading(false);
            },
        });
    };

    return (isSuperUser &&
        <>
            <ResetDialog open={open} isLoading={isLoading} onReset={handleReset} onCancel={closeDialog} />
            <div onClick={openDialog} role='button'>
                <NavigationCard
                    title={tr('resetTitle')}
                    desc={tr('resetTitle')}
                />
            </div>
        </>
    )
}
