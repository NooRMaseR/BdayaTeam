'use client';

import AddPhotoAlternateIcon from '@mui/icons-material/AddPhotoAlternate';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';
import { useTranslations } from 'next-intl';
import Image from 'next/image';
import React from 'react';

type Props = {
    images?: File[];
    onChange: (files: File[]) => void;
};

export default function ImageUploadWithPreviews({ images = [], onChange }: Props) {
    const [previewImages, setPreviewImages] = React.useState<string[]>([]);
    const tr = useTranslations("tasksPage");

    React.useEffect(() => { 
        const urls = images.map(image => URL.createObjectURL(image));
        setPreviewImages(urls);
        return () => {
            urls.forEach(url => URL.revokeObjectURL(url));
        }
    }, [images]);
    
    const handleAppend = (e: React.ChangeEvent<HTMLInputElement>) => {
        const newFiles = e.target.files;
        if (!newFiles || newFiles.length === 0) return;

        const dt = new DataTransfer();
        images.forEach(f => dt.items.add(f));
        Array.from(newFiles).forEach(f => dt.items.add(f));

        onChange(Array.from(dt.files));
        e.target.value = '';
    };

    const handleRemove = (indexToRemove: number) => {
        const newArray = images.filter((_, i) => i !== indexToRemove);
        onChange(newArray);
    };

    return (
        <div className="flex flex-col gap-4">
            {previewImages.length > 0 && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {previewImages.map((file, index) => (
                        <div key={index} className="relative group rounded-xl overflow-hidden border border-slate-200 aspect-square bg-slate-50">
                            <Image
                                src={file} 
                                alt={`preview-${index}`}
                                fill
                                className="w-full h-full object-cover"
                            />
                            
                            <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-start justify-end p-1">
                                <IconButton 
                                    size="small" 
                                    onClick={() => handleRemove(index)} 
                                    sx={{ color: 'white', bgcolor: 'rgba(0,0,0,0.5)', '&:hover': { bgcolor: 'red' } }}
                                >
                                    <CloseIcon fontSize="small" />
                                </IconButton>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <div>
                <input
                    id="image-upload-input"
                    type="file"
                    accept="image/*"
                    multiple
                    className="hidden"
                    onChange={handleAppend}
                />
                <label 
                    htmlFor="image-upload-input"
                    className="inline-flex items-center gap-2 px-4 py-2 border-2 border-dashed border-blue-400 text-blue-600 rounded-lg cursor-pointer hover:bg-blue-50 transition-colors font-medium text-sm"
                >
                    <AddPhotoAlternateIcon fontSize="small" />
                    {tr("addImages")}
                </label>
            </div>
        </div>
    );
}