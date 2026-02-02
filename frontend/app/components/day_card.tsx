'use client';

import { Button, Card, CardActions, CardContent, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, IconButton } from '@mui/material';
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
// import type { AttendanceDay } from '@/app/utils/api_types_helper';
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import DeleteIcon from "@mui/icons-material/Delete";
import { DatePicker } from "@mui/x-date-pickers";
import EditIcon from "@mui/icons-material/Edit";
import AddIcon from "@mui/icons-material/Add";
import { API } from '@/app/utils/api.client';
import { toast } from 'sonner';
import React from 'react';
import dayjs from 'dayjs';
import { components } from '../generated/api_types';

type AttendanceDay = components['schemas']['AttendanceDays'];
type DayCardProps = {
    day: AttendanceDay; 
    onDelete: (date: string) => void;
    track_name: string;
}

function DayCard({ day, onDelete, track_name }: DayCardProps) {
    const [dayState, setDayState] = React.useState<string>(day.day);
    const [dlgOpen, setDlgOpen] = React.useState<boolean>(false);

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
                loading: "Updating.....",
                success: (date) => `Date Update to ${date} successfully`,
                error: "somthing went wrong",
            }
        );
    }

    return (
        <>
            <Dialog open={dlgOpen}>
                <DialogTitle><p>Editing {dayState} </p></DialogTitle>
                <DialogContent>
                    <LocalizationProvider dateAdapter={AdapterDayjs}>
                        <DatePicker defaultValue={dayjs(dayState)} onChange={(e) => setDayState(e?.format("YYYY-MM-DD") || day.day)} />
                    </LocalizationProvider>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => saveDay()} >Save</Button>
                    <Button onClick={() => setDlgOpen(false)} >Cancle</Button>
                </DialogActions>
            </Dialog>
            <Card sx={{ width: "20rem", mb: "1rem" }}>
                <CardContent>
                    <p className='text-center'>{new Date(dayState).toLocaleDateString('en-US', { weekday: "long" })} - {dayState}</p>
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
                loading: "Adding.....",
                success: (date) => `Date ${date} created successfully`,
                error: "somthing went wrong",
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
                loading: "Deleting.....",
                success: "Date deleted successfully",
                error: "somthing went wrong",
            }
        );
    }

    return (
        <div className='mt-7 w-full flex justify-center flex-col items-center'>
            <Dialog open={confDlgOpen}>
                <DialogTitle><p>Delete?</p></DialogTitle>
                <DialogContent>
                    <DialogContentText>Are you Sure That you want to delete this day?</DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={deleteDay} >Yes</Button>
                    <Button onClick={() => setConfDlgOpen(false)} >Cancle</Button>
                </DialogActions>
            </Dialog>
            <Dialog open={dlgDate.open}>
                <DialogTitle><p>Add a new Attendance</p></DialogTitle>
                <DialogContent>
                    <LocalizationProvider dateAdapter={AdapterDayjs}>
                        <DatePicker onChange={(e) => setDlgDate(pre => ({ open: true, date: (e?.format("YYYY-MM-DD") || pre.date) }))} />
                    </LocalizationProvider>
                </DialogContent>
                <DialogActions>
                    <Button onClick={saveDay}>Save</Button>
                    <Button onClick={() => setDlgDate(pre => ({ open: false, date: pre.date }))}>Cancle</Button>
                </DialogActions>
            </Dialog>
            {days?.map(day => <DayCard track_name={ track } day={day} key={day?.id} onDelete={(e) => { setConfDlgOpen(true); setConfDlgDate(e); }} />)}
            <Button variant='contained' onClick={() => setDlgDate({ open: true, date: "" })}>
                Add
                <AddIcon />
            </Button>
        </div>
    )
}