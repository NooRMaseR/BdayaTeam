import { Link } from '@/i18n/navigation'
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';

export default function SessionTimeoutDialog({open}: {open: boolean}) {
    return (
        <Dialog open={open}>
            <DialogTitle>Opps!!</DialogTitle>
            <DialogContent>
                <DialogContentText>Session Timeout, Please Login Again</DialogContentText>
            </DialogContent>
            <DialogActions>
                <Link href='/login'>
                    <Button variant='contained'>Go To Login</Button>
                </Link>
            </DialogActions>
        </Dialog>
    )
}
