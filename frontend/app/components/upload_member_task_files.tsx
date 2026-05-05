'use client';

import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import CloseIcon from '@mui/icons-material/Close';
import AddIcon from '@mui/icons-material/Add';
import Tooltip from '@mui/material/Tooltip';

import { validateTaskFiles } from '../utils/api.client';
import { useTranslations } from 'next-intl';
import React from 'react'

type PopulatedFilesListProps = {
    selectedFiles?: string[];
    onClear: () => void;
    onRemoveFile: (index: number) => void;
};

type UploadMemberTaskFilesProps = PopulatedFilesListProps & {
    extensions?: string[];
    onFileChange: (e: React.ChangeEvent<HTMLInputElement, HTMLInputElement>) => void;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    [key: string]: any;
}

function UploadDropzone() {
    const tr = useTranslations('taskPage');
    return (
        <label 
            htmlFor="task-file-input" 
            className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-slate-300 rounded-xl dark:hover:bg-(--dark-color) hover:bg-slate-50 hover:border-blue-500 transition-colors cursor-pointer group"
        >
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <CloudUploadIcon className="w-8 h-8 mb-2 text-slate-400 group-hover:text-blue-500 transition-colors" />
                <Typography variant="body2" color="text.secondary">
                    <span className="font-semibold text-blue-600">{ tr('upload_title') }</span>
                </Typography>
                <Typography variant="subtitle1" color="text.secondary">
                    <span className="font-semibold text-blue-600">{ tr('upload_hint') }</span>
                </Typography>
            </div>
        </label>
    );
}

function PopulatedFilesList({ selectedFiles, onClear, onRemoveFile }: PopulatedFilesListProps) {
    return (
        <div className="border border-slate-200 rounded-xl p-4 dark:bg-(--dark-color) bg-slate-50 flex flex-col gap-2">
            <div className="flex justify-between items-center mb-2 border-b border-slate-200 pb-2">
                <div className="flex items-center gap-3">
                    <Typography variant="caption" fontWeight="bold" color="text.secondary" className="uppercase tracking-wider">
                        {selectedFiles?.length} File(s) Selected
                    </Typography>
                    
                    <Tooltip title="Add more files">
                        <label 
                            htmlFor="task-file-input" 
                            className="cursor-pointer inline-flex items-center justify-center p-1 bg-blue-100 text-blue-600 hover:bg-blue-200 dark:bg-blue-900/30 dark:hover:bg-blue-900/50 rounded transition-colors"
                        >
                            <AddIcon fontSize="small" />
                        </label>
                    </Tooltip>
                </div>

                <Tooltip title="Clear All">
                    <IconButton size="small" onClick={onClear} color="error" sx={{ padding: '4px' }}>
                        <DeleteOutlineIcon fontSize="small" />
                    </IconButton>
                </Tooltip>
            </div>
            
            <div className="flex flex-col gap-2 max-h-40 overflow-y-auto pr-1">
                {Array.from(selectedFiles!).map((file, i) => (
                    <div key={i} className="flex items-center gap-3 dark:bg-(--dark-color) bg-white border border-slate-200 p-2 rounded-lg group">
                        <AttachFileIcon fontSize="small" className="text-slate-400" />
                        <Typography variant="body2" className="truncate flex-1 font-medium">
                            {(file as unknown as File).name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                            {((file as unknown as File).size / 1024 / 1024).toFixed(2)} MB
                        </Typography>
                        
                        <IconButton 
                            size="small" 
                            onClick={() => onRemoveFile(i)} 
                            color="error" 
                            sx={{ padding: '4px', opacity: 0.6, '&:hover': { opacity: 1 } }}
                        >
                            <CloseIcon fontSize="small" />
                        </IconButton>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default function UploadMemberTaskFiles({selectedFiles, extensions, onClear, onRemoveFile, onFileChange, ...registerProps}: UploadMemberTaskFilesProps) {
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
                <PopulatedFilesList selectedFiles={selectedFiles} onClear={onClear} onRemoveFile={onRemoveFile} />
            )}
        </div>
    );
}
