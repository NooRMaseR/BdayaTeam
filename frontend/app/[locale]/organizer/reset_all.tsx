'use client';

import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from '@mui/material';
import NavigationCard from '../../components/navigation_card';
import { API } from '../../utils/api.client';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { toast } from 'sonner';
import React from 'react';

export default function ResetAll() {
    const [open, setOpen] = React.useState<boolean>(false);
    const [isLoading, setIsLoading] = React.useState<boolean>(false);
    const navigation = useRouter();
    const tr = useTranslations('organizerPage');

    const openDialog = () => setOpen(true);
    const closeDialog = () => setOpen(false);
    const handleReset = () => {
        setIsLoading(true);
        toast.promise(API.DELETE('/api/reset/'), {
            loading: "Deleteing....",
            success() {
                closeDialog();
                navigation.refresh();
                return "Reset Successfully";
            },
            error: "somthing went wrong, please try again later",
            finally() {
                setIsLoading(false);
            },
        });
    }
    return (
        <>
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
                    <Button variant='contained' onClick={closeDialog} loading={isLoading}>{tr('cancel')}</Button>
                    <Button variant='outlined' color='error' onClick={handleReset} loading={isLoading}>{tr('reset')}</Button>
                </DialogActions>
            </Dialog>
            <div onClick={openDialog}>
                <NavigationCard
                    title={tr('resetTitle')}
                    desc={tr('resetTitle')}
                />
            </div>
        </>
    )
}
