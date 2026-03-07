'use client';

import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import Button from '@mui/material/Button';

type TaskShowButtonProps = {
    task_id: number;
    fileName?: string; 
}

export default function TaskShowButton({ task_id, fileName = "Attachment" }: TaskShowButtonProps) {
    return (
        <Button 
            component="a" 
            target='_blank' 
            href={`${process.env.NEXT_PUBLIC_API_URL}/api/member/protected_media/tasks/${task_id}/`} 
            variant="outlined" 
            startIcon={<OpenInNewIcon />}
            sx={{ textTransform: 'none', borderRadius: 2 }}
        >
            Open {fileName}
        </Button>
    );
}