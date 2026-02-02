'use client';

import { Button, CircularProgress, Box } from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import { useEffect, useState } from 'react';
import { API } from '../utils/api.client';
import Image from 'next/image';

export default function SmartTaskLoader({ task_id }: { task_id: number }) {
    const [contentType, setContentType] = useState<string>('');
    const [contentDisposition, setContentDisposition] = useState<string>('');
    const [fileName, setFileName] = useState<string>('');
    const [hasError, setHasError] = useState<boolean>(false);
    const [fileContent, setFileContent] = useState<string | ''>('');
    
    useEffect(() => {
        const req = async () => {

            const { response, data, error } = await API.GET(
                "/api/member/protected_media/tasks/{task_id}/",
                {
                    params: { path: { task_id } },
                    parseAs: "blob"
                }
            );
            if (error) {
                console.error(error);
                setHasError(error);
            } else {
                setContentType(response.headers.get('Content-Type') || '');
                setContentDisposition(response.headers.get('Content-Disposition') || '');
                setFileName(contentDisposition?.split('filename=')[1] || '');
                setFileContent(URL.createObjectURL(data));
            }
        };
        req();
    }, [task_id, contentDisposition]);

    if (hasError) {
        return <h1>An Error Ocurred, please try again later</h1>
    }

    if (!fileContent) {
        return <CircularProgress />
    }

    // case Image
    if (contentType?.startsWith('image/')) {
        return <Image width={100} height={100} src={fileContent} alt={fileName} style={{position: "relative", width: 'auto', height: 'auto'}}/>;
    }

    // case PDF //! note that it downlods automaticly
    if (contentType === 'application/pdf') {
        return (
            <Box height={500} width="100%" border={1} borderColor="grey.300">
                <embed type={contentType} src={fileContent} width="100%" height="100%" style={{ border: 'none' }} />
            </Box>
        );
    }

    // case others
    return (
        <Button component={"a"} download={true} href={fileContent} variant="outlined" startIcon={<DownloadIcon />}>
            Download {fileName}
        </Button>
    );
}

