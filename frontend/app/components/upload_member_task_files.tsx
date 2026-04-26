'use client';

import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';

import { validateTaskFiles } from '../utils/api.client';
import { useTranslations } from 'next-intl';
import React from 'react'

type PopulatedFilesListProps = {
    selectedFiles?: string[];
    onClear: () => void;
};

type UploadMemberTaskFilesProps = PopulatedFilesListProps & {
    extensions?: string[];
    onFileChange: (e: React.ChangeEvent<HTMLInputElement, HTMLInputElement>) => void;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    [key: string]: any;
}

function UploadDropzone() {
    return (
        <label 
            htmlFor="task-file-input" 
            className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-slate-300 rounded-xl dark:hover:bg-(--dark-color) hover:bg-slate-50 hover:border-blue-500 transition-colors cursor-pointer group"
        >
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <CloudUploadIcon className="w-8 h-8 mb-2 text-slate-400 group-hover:text-blue-500 transition-colors" />
                <Typography variant="body2" color="text.secondary">
                    <span className="font-semibold text-blue-600">Click to upload</span>
                </Typography>
            </div>
        </label>
    );
}

function PopulatedFilesList({ selectedFiles, onClear }: PopulatedFilesListProps) {
    return (
        <div className="border border-slate-200 rounded-xl p-4 dark:bg-(--dark-color) bg-slate-50 flex flex-col gap-2">
            <div className="flex justify-between items-center mb-2">
                <Typography variant="caption" fontWeight="bold" color="text.secondary" className="uppercase tracking-wider">
                    {selectedFiles?.length} File(s) Selected
                </Typography>
                <IconButton size="small" onClick={onClear} color="error">
                    <DeleteOutlineIcon fontSize="small" />
                </IconButton>
            </div>
            
            <div className="flex flex-col gap-2 max-h-40 overflow-y-auto">
                {Array.from(selectedFiles!).map((file, i) => (
                    <div key={i} className="flex items-center gap-2 dark:bg-(--dark-color) bg-white border border-slate-200 p-2 rounded-lg">
                        <AttachFileIcon fontSize="small" className="text-slate-400" />
                        <Typography variant="body2" className="truncate flex-1 font-medium">
                            {(file as unknown as File).name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                            {((file as unknown as File).size / 1024 / 1024).toFixed(2)} MB
                        </Typography>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default function UploadMemberTaskFiles({selectedFiles, extensions, onClear, onFileChange, ...registerProps}: UploadMemberTaskFilesProps) {
    const tr = useTranslations('taskPage');

    return (
        <div className="w-full">
            <input
                id="task-file-input"
                type="file"
                className="hidden"
                accept={extensions?.map(ext => `.${ext}`)?.join(',')}
                multiple
                {...registerProps}
                onChange={(e) => validateTaskFiles(e, extensions, onFileChange, tr)}
            />

            {!selectedFiles || selectedFiles.length === 0 ? (
                <UploadDropzone />
            ) : (
                <PopulatedFilesList selectedFiles={selectedFiles} onClear={onClear} />
            )}
        </div>
    );
}
