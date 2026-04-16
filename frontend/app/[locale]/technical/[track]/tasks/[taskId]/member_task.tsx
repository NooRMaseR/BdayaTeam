'use client';

import VisibilityIcon from '@mui/icons-material/Visibility';
import CheckIcon from '@mui/icons-material/CheckCircle';
import ListItemText from '@mui/material/ListItemText';
import Typography from '@mui/material/Typography';
import ListItem from '@mui/material/ListItem';
import Tooltip from '@mui/material/Tooltip';
import Avatar from '@mui/material/Avatar';
import Paper from '@mui/material/Paper';
import List from '@mui/material/List';
import Chip from '@mui/material/Chip';

import type { MemberTaskItemProps, TaskShowCaseProps } from '@/app/components/task_show_case';
import TaskShowCase from '@/app/components/task_show_case';
import { checkLateStatus } from "@/app/utils/dayjs.client";
import { useLocale, useTranslations } from 'next-intl';
import useWebSocket from 'react-use-websocket';
import React from 'react';

type MembersRecivedTaskItemProps = {
    task: MemberTaskItemProps['tasksRecived'][0];
    onClick: (task: MemberTaskItemProps['tasksRecived'][0]) => void;
    showSigned?: boolean;
    overrideText?: { primary?: React.ReactNode, secondary?: React.ReactNode };
    viewer?: string;
}

type SecondaryActionUIProps = {
    lateStatus: string;
    lateString: string;
    viewer?: string;
}

function SecondaryActionUI({lateStatus, lateString, viewer}: SecondaryActionUIProps) {
    return (
    <div className="flex flex-col items-end gap-1">
        {lateStatus === "late" && (
            <Typography color='error' variant="caption" fontWeight="bold">
                {lateString}
            </Typography>
        )}
            
        {viewer && (
            <Tooltip title={`${viewer} is currently grading this task`} placement="left">
                <Chip
                    size="small"
                    color="warning"
                    variant="outlined"
                    icon={<VisibilityIcon fontSize="small" className="animate-pulse" />}
                    label={`${viewer} is reviewing...`}
                    sx={{
                        borderColor: 'orange',
                        color: 'orange',
                        backgroundColor: 'rgba(255, 165, 0, 0.05)',
                        '.MuiChip-icon': { color: 'orange' }
                    }}
                />
            </Tooltip>
        )}
        </div>
    )
};

export function MembersRecivedTaskItem({ task, onClick, showSigned = false, overrideText, viewer }: MembersRecivedTaskItemProps) {
    const tr = useTranslations('taskPage');
    const locale = useLocale();
    const late = checkLateStatus(task.task.expires_at, locale, task.recived_at, true);
    const lateString = tr('late', { time: late.from });


    return (
        <ListItem
            onClick={() => onClick(task)}
            className={`transition-colors border-b border-slate-100 last:border-0 cursor-pointer rounded-2xl ${
                viewer 
                    ? "bg-orange-50/50 dark:bg-orange-900/10 hover:bg-orange-100 dark:hover:bg-orange-900/20" 
                    : "dark:hover:bg-[#373737] hover:bg-gray-300"
            }`}
            secondaryAction={<SecondaryActionUI lateStatus={late.status} lateString={lateString} viewer={viewer} />}
        >
            <div className="flex items-center gap-4 w-full py-2">
                {showSigned && task.signed && (
                    <CheckIcon fontSize="medium" sx={{color: "green"}} />
                )}
                
                <Avatar sx={{ width: 32, height: 32, bgcolor: viewer ? 'warning.main' : 'primary.light', fontSize: '1rem' }}>
                    {task.member.name[0].toUpperCase()}
                </Avatar>
                
                <ListItemText
                    primary={overrideText?.primary ?? task.member.name}
                    secondary={overrideText?.secondary ?? task.member.code}
                    slotProps={{ primary: { fontWeight: 'medium' } }}
                />
            </div>
        </ListItem>
    )
}

export default function MembersRecivedTasks({ tasksRecived, track }: MemberTaskItemProps) {
    const [selectedTask, setSelectedTask] = React.useState<TaskShowCaseProps['task'] | null>(null);
    const [tasks, setTasks] = React.useState<MemberTaskItemProps['tasksRecived']>(tasksRecived);
    const [viewers, setViewers] = React.useState<Record<number, string>>({});
    const [open, setOpen] = React.useState<boolean>(false);
    const tr = useTranslations('taskPage');

    const { sendJsonMessage } = useWebSocket(`${process.env.NEXT_PUBLIC_WEBSOCKET_URL}/technical/live-online-tasks/${track}/`, {
        shouldReconnect: () => true,
        reconnectAttempts: 4,
        reconnectInterval: 3000,
        onMessage(event) {
            try {
                const payload = JSON.parse(event.data);

                if (payload && payload.type === "view" && payload.data && payload.data.task_id && payload.viewer) {
                    const data = payload.data;
                    setViewers(pre => {
                        const newViewer = { ...pre };
                        if (data.viewing) {
                            newViewer[data.task_id] = payload.viewer;
                        } else {
                            delete newViewer[data.task_id];
                        }
                        return newViewer;
                    });
                } else if (payload && payload.type === "delete" && payload.data && payload.data.task_id) {
                    const data = payload.data;
                    setTasks(pre => pre.filter(task => task.id !== data.task_id));
                    setViewers(prevViewers => {
                        const newViewers = { ...prevViewers };
                        delete newViewers[data.task_id];
                        return newViewers;
                    });
                }
            } catch {
                console.error("Faild to parse json");
            }
        },
    });

    const openDlg = (task: MembersRecivedTaskItemProps['task']) => {
        setSelectedTask(task);
        setOpen(true);
        sendJsonMessage({
            type: "view",
            data: {
                task_id: task.id,
                viewing: true,
            }
        });
    };

    const closeDlg = () => {
        setOpen(false);
        if (selectedTask)
            sendJsonMessage({
                type: "view",
                data: {
                    task_id: selectedTask.id,
                    viewing: false,
                }
            });

        setSelectedTask(null);
    };

    const onSign = (signedId: number) => {
        closeDlg();
        sendJsonMessage({
            type: "delete",
            data: {
                task_id: signedId,
                viewing: false,
            }
        });
    };

    return (
        <div>
            <Typography variant="h6" fontWeight="bold" sx={{ mb: 2, px: 1 }}>
                {tr('submited')} ({tasks.length})
            </Typography>
            <Paper elevation={0} className="border border-slate-200 rounded-xl overflow-hidden bg-white mx-4 my-2">
                <TaskShowCase open={open} task={selectedTask} onSuccess={onSign} onClose={closeDlg} />
                {tasksRecived.length > 0 && (
                    <List disablePadding>
                        {tasks.map(task =>
                            <MembersRecivedTaskItem key={task.id} task={task} onClick={openDlg} viewer={viewers[task.id]} />
                        )}
                    </List>
                )}
            </Paper>
        </div>
    )
}