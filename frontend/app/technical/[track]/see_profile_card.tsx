'use client';

import { Button, Dialog, DialogActions, DialogContent, DialogTitle, TextField } from '@mui/material';
import NavigationCard from '@/app/components/navigation_card';
import { useRouter } from 'next/navigation';
import React from 'react'

export default function SeeProfileCard() {
    const [open, setOpen] = React.useState<boolean>(false);
    const [code, setCode] = React.useState<string>('');
    const navigation = useRouter();

    const handleCloseDialog = () => setOpen(false);
    const handleOpenDialog = () => setOpen(true);

    const seeMember = () => navigation.push(`/profile/${code}`);
    const handleOnChange = (e: React.ChangeEvent<HTMLInputElement>) => setCode(e.target.value);

    return (
        <>
            <Dialog open={open} scroll='paper'>
                <DialogTitle>Enter The Member Code</DialogTitle>
                <DialogContent sx={{marginBlock: '1rem'}}>
                    <TextField onChange={handleOnChange} label="member code" required fullWidth />
                </DialogContent>
                <DialogActions>
                    <Button variant='contained' onClick={handleCloseDialog}>Cancel</Button>
                    <Button color='success' variant='contained' onClick={seeMember} >Go</Button>
                </DialogActions>
            </Dialog>
            <div onClick={handleOpenDialog}>
                <NavigationCard
                    title="See member Profile"
                    desc="See Member Profile By Member's Code"
                />
            </div>
        </>
    )
}
