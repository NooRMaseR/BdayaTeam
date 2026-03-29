'use client';

import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Dialog from '@mui/material/Dialog';
import Button from '@mui/material/Button';

import LocaledTextField from '@/app/components/localed_textField';
import NavigationCard from '@/app/components/navigation_card';
import { useRouter } from '@/i18n/navigation';
import { useTranslations } from 'next-intl';
import React from 'react';

export default function SeeProfileCard() {
    const [open, setOpen] = React.useState<boolean>(false);
    const [code, setCode] = React.useState<string>('');
    const tr = useTranslations("technicalPage");
    const navigation = useRouter();

    const handleCloseDialog = () => setOpen(false);
    const handleOpenDialog = () => setOpen(true);

    const seeMember = (e: React.SubmitEvent<HTMLFormElement>) => {
        e.preventDefault();
        navigation.push(`/profile/${code}`);
    };
    const handleOnChange = (e: React.ChangeEvent<HTMLInputElement>) => setCode(e.target.value);

    return (
        <>
            <Dialog open={open} scroll='paper'>
                <DialogTitle>{tr('enterMemberCode')}</DialogTitle>
                <form onSubmit={seeMember}>
                    <DialogContent sx={{marginBlock: '1rem'}}>
                        <LocaledTextField onChange={handleOnChange} label={tr('memberCode')} required fullWidth />
                    </DialogContent>
                    <DialogActions>
                        <Button variant='contained' onClick={handleCloseDialog}>{tr('cancel')}</Button>
                        <Button color='success' variant='contained' type='submit'>{tr('go')}</Button>
                    </DialogActions>
                </form>
            </Dialog>
            <div onClick={handleOpenDialog}>
                <NavigationCard
                    title={tr('seeProfile')}
                    desc={tr('seeProfileDesc')}
                />
            </div>
        </>
    )
}
