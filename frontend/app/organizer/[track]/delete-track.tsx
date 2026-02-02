'use client';

import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Typography } from '@mui/material';
import NavigationCard from '@/app/components/navigation_card';
import { API } from '@/app/utils/api.client';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import React from 'react'

interface DeleteTrackProps {
    name: string;
}

export default function DeleteTrack({ name }: DeleteTrackProps) {
    const [open, setOpen] = React.useState<boolean>(false);
    const openDialog = () => setOpen(true);
    const closeDialog = () => setOpen(false);
    const navigation = useRouter();

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
                loading: "Deleting.....",
                success: `Track ${name} has been deleted`,
                error: "Somthing went wrong",
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
                    Delete {name}
                </DialogTitle>
                <DialogContent>
                    <DialogContentText component={'span'}>
                        <Typography variant='h6'>Are You Sure You want to delete {name}?</Typography>
                        <Typography color='error'>This will delete all members and tasks related to this Track</Typography>
                    </DialogContentText>
                </DialogContent>
                <DialogActions sx={{ gap: ".5rem" }}>
                    <Button variant='contained' onClick={closeDialog}>Cancel</Button>
                    <Button variant='outlined' color='error' onClick={performDeleteTrack}>Delete</Button>
                </DialogActions>
            </Dialog>
            <div onClick={openDialog}>
                <NavigationCard
                    title={`Delete ${name}`}
                    desc="Danger"
                />
            </div>
        </>
    )
}

