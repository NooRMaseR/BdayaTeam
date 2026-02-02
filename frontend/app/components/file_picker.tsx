import React from 'react';
import Image from 'next/image';

interface FileProps {
    accept: `${string}/${string}`;
    preview?: string | null;
}

export default function FilePicker({ accept, preview, ...props }: FileProps & React.InputHTMLAttributes<HTMLInputElement>) {
    let realPreview: typeof preview = '';
    if (preview?.toString().startsWith("public/")) {
        realPreview = `${process.env.NEXT_PUBLIC_MEDIA_URL}${preview}`;
    } else {
        realPreview = preview;
    }
    
    return (
        <div>
            {realPreview ? (
                <div className='border-dashed border-b-slate-400'>
                    <Image src={realPreview} width={200} height={200} alt={"Team Logo"} unoptimized />
                </div>
            ) : null}
            <input type="file" accept={accept} {...props} />
        </div>
    )
}
