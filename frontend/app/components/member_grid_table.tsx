/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import type { GridRowModel, GridColDef, GridColumnGroupingModel, GridCellParams } from '@mui/x-data-grid';
import { AttendanceStatus, MemberStatus } from '../utils/api_types_helper';
import useWebSocket, { ReadyState } from "react-use-websocket";
import type { GridRowsProp } from '@mui/x-data-grid';
import { useTranslations } from 'next-intl';
import { DataGrid } from '@mui/x-data-grid';
import { useMemo, useState } from 'react';
import { Link } from '@/i18n/navigation';
import { Button } from '@mui/material';
import API from '../utils/api.client';
import { toast } from 'sonner';

type GridProps = {
    rows: GridRowsProp;
    columns: GridColDef[];
    columnGroupingModel?: GridColumnGroupingModel;
    track: string;
    forTech?: boolean;
    disableWebSocket?: boolean;
}

type SocketResponse = {
    data: {
        by: string;
        code: string;
        changedKey: string;
        changedValue: string | number;
    }
}

const ACTIONS_COLUMN_BASE: Omit<GridColDef, 'headerName' | 'renderCell'> = {
    align: "center",
    headerAlign: "center",
    field: "actions",
    width: 120,
    filterable: false,
    sortable: false,
};

export default function MembersGridTable({ rows, columns, columnGroupingModel, track, forTech = false, disableWebSocket = false }: GridProps) {
    const tr = useTranslations('showMembersPage');
    const trackReadableName = track.replaceAll("%20", ' ');
    const [localRows, setLocalRows] = useState<GridRowsProp>(rows);
    const memoColumns = useMemo<GridColDef[]>(() => [{
        ...ACTIONS_COLUMN_BASE,
        headerName: tr("actions"),
        renderCell(params) {
            return <Link href={`/profile/${params.id}`}>
                <Button variant='contained'>{tr('profile')}</Button>
            </Link>
        },
    }, ...columns], [columns, tr]);

    const ws_url = disableWebSocket ? null : `${process.env.NEXT_PUBLIC_WEBSOCKET_URL}/${forTech ? "technical" : "organizer"}/edit-member/${track}/`;
    const { sendJsonMessage, readyState } = useWebSocket(ws_url, {
        shouldReconnect: () => true,
        reconnectAttempts: 10,
        reconnectInterval: 3000,
        onMessage(event) {
            try {
                const data: SocketResponse = JSON.parse(event.data);
                if (data) {
                    const { by, code, changedKey, changedValue } = data.data;
                    setLocalRows((prevRows) => {
                        const rowIndex = prevRows.findIndex(row => row.code == code);

                        if (rowIndex === -1) return prevRows;

                        const newRows = [...prevRows];
                        newRows[rowIndex] = {
                            ...newRows[rowIndex],
                            [changedKey]: changedValue,
                        };
                        if (by && changedKey.endsWith("_date")) {
                            const key = changedKey.replace("_date", '_by');
                            newRows[rowIndex][key] = by;
                        } else if (by && changedKey.startsWith("task_deg_")) {
                            const id = parseInt(changedKey.replace("task_deg_", ''));
                            newRows[rowIndex][`task_signed_by_${id}`] = by;
                        }
                        return newRows;
                    });
                }
            } catch {
                console.error("field to parse websocket json");
            }
        },
    });

    const handleOrg = async (newRow: GridRowModel, oldRow: GridRowModel, changedKey: any) => await toast.promise<GridRowModel>(async () => {

        const changedValue = newRow[changedKey];
        const isAttendance: boolean = Object.values(AttendanceStatus).includes(changedValue);
        const hasExcuse: boolean = changedKey.endsWith("_excuse");

        const { response } = await
            API.POST(`/api/organizer/members/{track_name}/`, {
                params: { path: { track_name: track } },
                body: {
                    code: newRow.code,
                    field: changedKey.replace(hasExcuse ? "_excuse" : "_date", '').replace("_by", ''),
                    value: hasExcuse ? newRow[changedKey.replace("_excuse", "_date")] : changedValue,
                    type: isAttendance || hasExcuse ? "attendance" : "data",
                    excuse: hasExcuse ? newRow[changedKey] : null
                }
            });

        if (response.ok) {
            return await Promise.resolve(newRow);
        }
        return await Promise.reject(oldRow);
    },
        {
            loading: tr('saving'),
            success: tr('saved'),
            error: tr('notSaved'),
        }
    ).unwrap();

    const handleTech = async (newRow: GridRowModel, oldRow: GridRowModel, changedKey: any) => await toast.promise<GridRowModel>(async () => {

        const changedValue = newRow[changedKey];
        const taskID = parseInt(changedKey?.replace("task_deg_", '').replace('task_notes_', '').replace("task_deg_", ''));
        const changedField = changedKey.includes('deg_') ? "degree" : "notes";

        const { response } = await
            API.PUT(`/api/technical/members/{track_name}/with-tasks/`, {
                params: { path: { track_name: track } },
                body: {
                    code: newRow.code,
                    task_id: taskID,
                    field: changedField,
                    value: changedValue,
                }
            });

        if (response.ok) {
            toast.success(tr('saved'));
            return await Promise.resolve(newRow);
        } else if (response.status === 404) {
            toast.error(tr("no_member_task"));
            return await Promise.reject(oldRow);
        }
        return await Promise.reject(oldRow);
    },
        {
            loading: tr('saving'),
        }
    ).unwrap();

    const handelProcess = async (newRow: GridRowModel, oldRow: GridRowModel) => {
        const changedKey = Object.keys(newRow).find(
            (key) => newRow[key] !== oldRow[key]
        );

        if (!changedKey) return oldRow;

        let updatedRow: GridRowModel;
        if (forTech) {
            updatedRow = await handleTech(newRow, oldRow, changedKey);
        } else {
            updatedRow = await handleOrg(newRow, oldRow, changedKey);
        }

        if (!disableWebSocket && updatedRow.code == newRow.code && updatedRow[changedKey] === newRow[changedKey]) {
            sendJsonMessage({
                type: "edit",
                data: {
                    code: newRow.code,
                    changedKey: changedKey,
                    changedValue: newRow[changedKey]
                }
            });
        };

        return updatedRow;
    };

    const colorizeCellsFunction = (params: GridCellParams<any, AttendanceStatus | MemberStatus>) => {
        switch (params.value) {
            case AttendanceStatus.ABSENT:
                return 'bg-[red] text-white';
            case AttendanceStatus.PRESENT:
                return 'bg-green-600 text-white';
            case AttendanceStatus.EXCUSED:
                return 'bg-yellow-300 text-black';
            case MemberStatus.WARNING1:
                return 'bg-yellow-300 text-black';
            case MemberStatus.WARNING2:
                return 'bg-yellow-300 text-black';
            case MemberStatus.NORMAL:
                return 'bg-blue-600 text-white';
            case MemberStatus.FIRED:
                return 'bg-[red] text-white';
            default:
                return '';
        };
    };

    const connectionStatus = {
        [ReadyState.CONNECTING]: 'Connecting...',
        [ReadyState.OPEN]: 'Live',
        [ReadyState.CLOSING]: 'Closing...',
        [ReadyState.CLOSED]: 'Offline',
        [ReadyState.UNINSTANTIATED]: 'Uninstantiated',
    }[readyState];

    return (
        <div className='h-[87svh] color-trans'>
            {!disableWebSocket && <div className="flex mb-1 text-sm text-gray-500">
                Status:
                <span className={readyState === ReadyState.OPEN ? 'text-green-500 ml-1 font-bold' : 'text-red-500 ml-1 font-bold'}>
                    {connectionStatus}
                </span>
            </div>}
            <DataGrid
                className='color-trans'
                rows={localRows}
                columns={memoColumns}
                label={tr('trackHead', { track: trackReadableName })}
                getCellClassName={colorizeCellsFunction}
                processRowUpdate={handelProcess}
                columnGroupingModel={columnGroupingModel}
                localeText={{
                    filterOperatorContains: tr('contains'),
                    filterOperatorDoesNotContain: tr('notContains'),
                    filterOperatorEquals: tr('equals'),
                    filterOperatorDoesNotEqual: tr('notEqual'),
                    filterOperatorStartsWith: tr('startsWith'),
                    filterOperatorEndsWith: tr('endsWith'),
                    filterOperatorIsEmpty: tr('isEmpty'),
                    filterOperatorIsNotEmpty: tr('isNotEmpty'),
                    filterOperatorIsAnyOf: tr('isAnyOf'),
                    paginationDisplayedRows: (params) => tr('totalRows', { from: params.from, to: params.to, count: params.count }),
                    paginationRowsPerPage: tr('perPage')
                }}
                showColumnVerticalBorder
                showCellVerticalBorder
                showToolbar
            />
        </div>
    )
}
