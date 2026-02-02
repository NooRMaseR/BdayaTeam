'use client';

import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from '@mui/material'
import NavigationCard from '../components/navigation_card'
import { useRouter } from 'next/navigation';
import { API } from '../utils/api.client';
import { toast } from 'sonner';
import React from 'react';

export default function ResetAll() {
    const [open, setOpen] = React.useState<boolean>(false);
    const [isLoading, setIsLoading] = React.useState<boolean>(false);
    const navigation = useRouter();

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
                <DialogTitle>Reset All</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        Are you sure you want to reset all?
                    </DialogContentText>
                    <DialogContentText color='error'>
                        this will delete (Tracks, Members, Tasks, Technicals)
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button variant='contained' onClick={closeDialog} loading={isLoading}>Cancel</Button>
                    <Button variant='outlined' color='error' onClick={handleReset} loading={isLoading}>Reset</Button>
                </DialogActions>
            </Dialog>
            <div onClick={openDialog}>
                <NavigationCard
                    title="Reset All"
                    desc="Reset All"
                />
            </div>
        </>
    )
}
