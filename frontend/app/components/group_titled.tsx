import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import Paper from '@mui/material/Paper';
import React from 'react'

type GroupTitledProps = {
    title: string;
    caption?: string;
    children: React.ReactNode
}

export default function GroupTitled({ title, caption, children }: GroupTitledProps) {
    return (
        <Paper elevation={0} className="p-6 border border-slate-200 rounded-2xl">
            <Typography variant="h6" fontWeight="bold" gutterBottom>
                {title}
            </Typography>
            {caption && <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                {caption}
            </Typography>}
            <Divider sx={{ mb: 3 }} />
            {children}
        </Paper>
    )
}
