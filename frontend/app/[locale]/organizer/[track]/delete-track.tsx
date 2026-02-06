'use client';

import DialogContentText from '@mui/material/DialogContentText';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import DialogTitle from '@mui/material/DialogTitle';
import Typography from '@mui/material/Typography';
import Dialog from '@mui/material/Dialog';
import Button from '@mui/material/Button';

import NavigationCard from '@/app/components/navigation_card';
import { useRouter } from '@/i18n/navigation';
import { API } from '@/app/utils/api.client';
import { toast } from 'sonner';
import React from 'react'
import { useTranslations } from 'next-intl';

interface DeleteTrackProps {
    name: string;
}

export default function DeleteTrack({ name }: DeleteTrackProps) {
    const [open, setOpen] = React.useState<boolean>(false);
    const openDialog = () => setOpen(true);
    const closeDialog = () => setOpen(false);
    const navigation = useRouter();
    const tr = useTranslations('trackPage');

    const performDeleteTrack = async () => {
        const success = await toast.promise<boolean>(async () => {
            const { response } = await API.DELETE("/api/tracks/{track_name}/delete/", {
                params: {path: {track_name: name}}
            });
            if (response.ok) {
                return await Promise.resolve(true);
            } else {
                return await Promise.reject(false);
            }
        },
            {
                loading: tr('deleting'),
                success: tr('trackDeleted', {name}),
                error: tr('wrong'),
            }
        ).unwrap();
        
        if (success) {
            navigation.replace("/organizer");
        }
    };

    return (
        <>
            <Dialog open={open} aria-hidden={open}>
                <DialogTitle variant='h6'>
                    {tr('deleteConf', {name})}
                </DialogTitle>
                <DialogContent>
                    <DialogContentText component={'span'}>
                        <Typography variant='h6'>{tr('deleteConfDesc', {name})}</Typography>
                        <Typography color='error'>{tr('deleteConfDesc2')}</Typography>
                    </DialogContentText>
                </DialogContent>
                <DialogActions sx={{ gap: ".5rem" }}>
                    <Button variant='contained' onClick={closeDialog}>{tr('cancel')}</Button>
                    <Button variant='outlined' color='error' onClick={performDeleteTrack}>{tr('delete')}</Button>
                </DialogActions>
            </Dialog>
            <div onClick={openDialog}>
                <NavigationCard
                    title={tr('deleteTitle', {name})}
                    desc={tr("deleteDesc")}
                />
            </div>
        </>
    )
}

