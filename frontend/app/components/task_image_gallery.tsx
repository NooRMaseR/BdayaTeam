'use client';

import Typography from '@mui/material/Typography';
import Backdrop from '@mui/material/Backdrop';
import { useState } from 'react';
import Image from 'next/image';

type TaskImageGalleryProps = {
    images?: string[];
    title: string;
};

export default function TaskImageGallery({ images, title }: TaskImageGalleryProps) {
    const [selectedImg, setSelectedImg] = useState<string | null>(null);

    if (!images || images.length === 0) return null;

    return (
        <div className="p-6 md:p-8 dark:bg-(--dark-color) bg-slate-50/50 border-t border-slate-200">
            <Typography variant="overline" color="primary" fontWeight="bold">
                {title}
            </Typography>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-3">
                {images.map((img, idx) => {
                    return (
                        <div
                            key={idx}
                            onClick={() => setSelectedImg(img)}
                            className="relative aspect-square rounded-xl overflow-hidden border border-slate-200 cursor-pointer group bg-white shadow-sm"
                        >
                            <Image
                                src={img}
                                fill
                                alt={`task-img-${idx}`}
                                unoptimized={process.env.NEXT_PUBLIC_UNOPTIMIZED == 'true'}
                                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                            />
                            <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors" />
                        </div>
                    );
                })}
            </div>

            <Backdrop open={!!selectedImg} onClick={() => setSelectedImg(null)} sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
                {selectedImg && (
                    <div className="relative w-full h-full p-8 md:p-16 flex justify-center items-center">
                        <Image
                            src={selectedImg}
                            alt="Expanded view"
                            fill
                            unoptimized={process.env.NEXT_PUBLIC_UNOPTIMIZED == 'true'}
                            className="object-contain drop-shadow-2xl" 
                        />
                    </div>
                )}
            </Backdrop>
        </div>
    );
}