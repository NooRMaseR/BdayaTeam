'use client';

import CircularProgress from '@mui/material/CircularProgress';
import DownloadIcon from '@mui/icons-material/Download';
import Button from '@mui/material/Button';

import { useEffect, useState } from 'react';
import { API } from '../utils/api.client';

export default function SmartTaskLoader({ task_id }: { task_id: number }) {
    const [fileName, setFileName] = useState<string>('');
    const [hasError, setHasError] = useState<boolean>(false);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [fileContent, setFileContent] = useState<string | ''>('');
    
    useEffect(() => {
        let active = true;
        let objectUrl: string | Blob | null = null;
        const req = async () => {

            const { response, data, error } = await API.GET(
                "/api/member/protected_media/tasks/{task_id}/",
                {
                    params: { path: { task_id } },
                    parseAs: "blob"
                }
            );

            if (!active) return;

            if (error) {
                setHasError(error);
            } else {
                const type = response.headers.get('Content-Type') || 'application/octet-stream';
                const disp = response.headers.get('Content-Disposition') || '';
                
                setFileName(disp.split('filename=')[1]?.replace(/"/g, '') || 'file');

                objectUrl = new Blob([data], { type: type });
                setFileContent(URL.createObjectURL(objectUrl));
            };
            setIsLoading(false);
        };
        req();
        return () => {
            active = false;
            if (objectUrl) {
                URL.revokeObjectURL(objectUrl as string);
            }
        };
    }, [task_id]);

    if (hasError) {
        return <h1>An Error Ocurred, please try again later</h1>
    }

    if (isLoading) {
        return <CircularProgress />
    }

    return (
        <Button component="a" target='_blank' href={fileContent} variant="outlined" startIcon={<DownloadIcon />}>
            Open {fileName}
        </Button>
    );
}

