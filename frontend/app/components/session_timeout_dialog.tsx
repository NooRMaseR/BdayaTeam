import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from '@mui/material'
import { Link } from '@/i18n/navigation'

export default function SessionTimeoutDialog({open}: {open: boolean}) {
    return (
        <Dialog open={open}>
            <DialogTitle>Opps!!</DialogTitle>
            <DialogContent>
                <DialogContentText>Session Timeout, Please Login Again</DialogContentText>
            </DialogContent>
            <DialogActions>
                <Link
                    href='/login'>
                    <Button variant='contained'>Go To Login</Button>
                </Link>
            </DialogActions>
        </Dialog>
    )
}
