'use client';

import DialogContentText from '@mui/material/DialogContentText';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Dialog from '@mui/material/Dialog';

import CardContent from '@mui/material/CardContent';
import CardActions from '@mui/material/CardActions';
import Card from '@mui/material/Card';

import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import EditIcon from "@mui/icons-material/Edit";
import AddIcon from "@mui/icons-material/Add";
import Button from '@mui/material/Button';

import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import type { components } from '../generated/api_types';
import DeleteIcon from "@mui/icons-material/Delete";
import { DatePicker } from "@mui/x-date-pickers";
import { API } from '@/app/utils/api.client';
import { useTranslations } from 'next-intl';
import { toast } from 'sonner';
import React from 'react';
import dayjs from 'dayjs';

type AttendanceDay = components['schemas']['AttendanceDays'];
type DayCardProps = {
    day: AttendanceDay; 
    onDelete: (date: string) => void;
    track_name: string;
}

function DayCard({ day, onDelete, track_name }: DayCardProps) {
    const [dayState, setDayState] = React.useState<string>(day.day);
    const [dlgOpen, setDlgOpen] = React.useState<boolean>(false);
    const tr = useTranslations('trackDayAddPage');
    const dtr = useTranslations('weekDays');

    const saveDay = () => {
        toast.promise<string | undefined>(async () => {
            const { response } = await API.PUT(`/api/organizer/attendance/{track_name}/days/`, {
                params: { path: { track_name } },
                body: { oldDay: day.day, newDay: dayState }
            });
            if (response.ok) {
                setDlgOpen(false);
                return await Promise.resolve(dayState);
            }
            return await Promise.reject(dayState);
        },
            {
                loading: tr('updating'),
                success: (date) => tr('updated', {date: date || ''}),
                error: tr('wrong'),
            }
        );
    }

    return (
        <>
            <Dialog open={dlgOpen}>
                <DialogTitle>{tr("editing", {dayState})}</DialogTitle>
                <DialogContent>
                    <LocalizationProvider dateAdapter={AdapterDayjs}>
                        <DatePicker defaultValue={dayjs(dayState)} onChange={(e) => setDayState(e?.format("YYYY-MM-DD") || day.day)} />
                    </LocalizationProvider>
                </DialogContent>
                <DialogActions>
                    <Button variant='contained' onClick={() => saveDay()}>{tr('save')}</Button>
                    <Button variant='contained' onClick={() => setDlgOpen(false)}>{tr('cancel')}</Button>
                </DialogActions>
            </Dialog>
            <Card sx={{ width: "20rem", mb: "1rem" }}>
                <CardContent>
                    <Typography sx={{textAlign: "center"}}>{dtr(new Date(dayState).toLocaleDateString('en-US', { weekday: "long" }))} - {dayState}</Typography>
                </CardContent>
                <CardActions sx={{ display: "flex", justifyContent: "center" }}>
                    <IconButton onClick={() => setDlgOpen(true)}>
                        <EditIcon />
                    </IconButton>
                    <IconButton onClick={() => onDelete(day.day)}>
                        <DeleteIcon color='error' />
                    </IconButton>
                </CardActions>
            </Card>
        </>
    )
}

export default function Days({ data, track }: { data?: AttendanceDay[], track: string }) {
    const [days, setDays] = React.useState<AttendanceDay[]>(data || []);
    const [confDlgOpen, setConfDlgOpen] = React.useState<boolean>(false);
    const [confDlgDate, setConfDlgDate] = React.useState<string>("");
    const [dlgDate, setDlgDate] = React.useState<{ open: boolean, date: string }>({ open: false, date: "" });
    const tr = useTranslations('trackDayAddPage');

    const saveDay = () => {
        toast.promise<string | undefined>(async () => {
            const { response, data } = await API.POST(`/api/organizer/attendance/{track_name}/days/`, { params: { path: { track_name: track } }, body: { day: dlgDate.date } });
            if (response.ok) {
                setDlgDate(pre => ({ open: false, date: pre.date }));
                setDays(pre => [...pre, data!])
                return await Promise.resolve(dlgDate.date);
            }
            return await Promise.reject(dlgDate.date);
        },
            {
                loading: tr('adding'),
                success: (date) => tr('dayCreated', {date: date || ''}),
                error: tr('wrong'),
            }
        );
    }

    const deleteDay = () => {
        toast.promise(async () => {
            const res = await API.DELETE(
                `/api/organizer/attendance/{track_name}/days/`,
                {
                    params: {
                        path: { track_name: track },
                        query: {day: confDlgDate}
                    }
                });
            if (res.response.ok) {
                setConfDlgOpen(false);
                setDays(pre => pre.filter(p => p.day != confDlgDate));
                return await Promise.resolve();
            }
            return await Promise.reject();
        },
            {
                loading: tr('deleting'),
                success: tr('dayDeleted'),
                error: tr('wrong'),
            }
        );
    }

    return (
        <div className='mt-7 w-full flex justify-center flex-col items-center'>
            <Dialog open={confDlgOpen}>
                <DialogTitle>{tr('deleteConf')}</DialogTitle>
                <DialogContent>
                    <DialogContentText>{tr('deleteConfDesc')}</DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={deleteDay} color='error' variant='contained'>{tr('delete')}</Button>
                    <Button onClick={() => setConfDlgOpen(false)} variant='contained'>{tr('cancel')}</Button>
                </DialogActions>
            </Dialog>
            <Dialog open={dlgDate.open}>
                <DialogTitle>{ tr('addAtten') }</DialogTitle>
                <DialogContent>
                    <LocalizationProvider dateAdapter={AdapterDayjs}>
                        <DatePicker onChange={(e) => setDlgDate(pre => ({ open: true, date: (e?.format("YYYY-MM-DD") || pre.date) }))} />
                    </LocalizationProvider>
                </DialogContent>
                <DialogActions>
                    <Button onClick={saveDay}>{tr('save')}</Button>
                    <Button onClick={() => setDlgDate(pre => ({ open: false, date: pre.date }))}>{tr('cancel')}</Button>
                </DialogActions>
            </Dialog>
            {days?.map(day => <DayCard track_name={ track } day={day} key={day?.id} onDelete={(e) => { setConfDlgOpen(true); setConfDlgDate(e); }} />)}
            <Button variant='contained' onClick={() => setDlgDate({ open: true, date: "" })}>
                {tr('add')}
                <AddIcon />
            </Button>
        </div>
    )
}