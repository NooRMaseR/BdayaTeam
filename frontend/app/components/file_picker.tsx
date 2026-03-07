'use client';

import React from 'react';
import Image from 'next/image';
import { useTranslations } from 'next-intl';

interface FileProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'accept'> {
    accept: `${string}/${string}` | string; 
    preview?: string | null;
}

const FilePicker = React.forwardRef<HTMLInputElement, FileProps>(({ accept, preview, ...props }, ref) => {
        const [isDragging, setIsDragging] = React.useState(false);
        const localRef = React.useRef<HTMLInputElement | null>(null);
        const tr = useTranslations("filePicker");

        const setRefs = (element: HTMLInputElement | null) => {
            localRef.current = element;
            if (typeof ref === 'function') {
                ref(element);
            } else if (ref) {
                ref.current = element;
            }
        };

        let realPreview = preview;
        if (preview?.startsWith("public/")) {
            realPreview = `${process.env.NEXT_PUBLIC_MEDIA_URL}${preview}`;
        }

        const handleDragOver = (e: React.DragEvent<HTMLLabelElement>) => {
            e.preventDefault();
            e.stopPropagation();
            setIsDragging(true);
        };

        const handleDragLeave = (e: React.DragEvent<HTMLLabelElement>) => {
            e.preventDefault();
            e.stopPropagation();
            setIsDragging(false);
        };

        const handleDrop = (e: React.DragEvent<HTMLLabelElement>) => {
            e.preventDefault();
            e.stopPropagation();
            setIsDragging(false);

            if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                if (localRef.current) {
                    localRef.current.files = e.dataTransfer.files;
                    
                    const event = new Event('change', { bubbles: true });
                    localRef.current.dispatchEvent(event);
                    
                    if (props.onChange) {
                        props.onChange({
                            target: localRef.current,
                            currentTarget: localRef.current,
                            preventDefault: () => {},
                            stopPropagation: () => {}
                        } as React.ChangeEvent<HTMLInputElement>);
                    }
                }
            }
        };

        return (
            <div className="w-full">
                <label 
                    onDragOver={handleDragOver}
                    onDragEnter={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={`
                        relative flex flex-col items-center justify-center w-full h-48 
                        border-2 border-dashed rounded-xl cursor-pointer 
                        transition-all duration-200 overflow-hidden group
                        ${realPreview 
                            ? 'border-transparent bg-gray-50' 
                            : isDragging 
                                ? 'border-blue-500 bg-blue-50'
                                : 'border-gray-300 hover:border-blue-500 hover:bg-blue-50/50'
                        }
                    `}
                >
                    {realPreview ? (
                        <>
                            <Image 
                                src={realPreview} 
                                alt="Preview" 
                                fill
                                style={{ objectFit: 'contain' }}
                                unoptimized 
                            />
                            <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                                <span className="text-white font-medium bg-black/50 px-4 py-2 rounded-lg backdrop-blur-sm">
                                    {tr('changeImg')}
                                </span>
                            </div>
                        </>
                    ) : (
                        <div className="flex flex-col items-center justify-center pt-5 pb-6 pointer-events-none">
                            <svg className={`w-10 h-10 mb-3 transition-colors ${isDragging ? 'text-blue-500' : 'text-gray-400 group-hover:text-blue-500'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                            </svg>
                            <p className="mb-2 text-sm text-gray-500">
                                <span className="font-semibold text-blue-600">{tr('toUpload')}</span> {tr('or')}
                            </p>
                            <p className="text-xs text-gray-400">
                                {accept.replace(/image\//g, '').toUpperCase().replace(/,/g, ', ')}
                            </p>
                        </div>
                    )}
                    
                    <input 
                        ref={setRefs}
                        type="file" 
                        accept={accept} 
                        className="hidden" 
                        {...props} 
                    />
                </label>
            </div>
        );
    }
);

FilePicker.displayName = 'FilePicker';
export default FilePicker;