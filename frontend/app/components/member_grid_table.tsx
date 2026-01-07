'use client';

import type { GridRowModel, GridColDef, GridRowsProp, GridColumnGroupingModel } from '@mui/x-data-grid';
import { AttendanceStatus, MemberStatus } from '../utils/api_types_helper';
import { DataGrid } from '@mui/x-data-grid';
import { API } from '../utils/api.client';
import { useMemo } from 'react';
import { toast } from 'sonner';

type GridProps = {
    rows: GridRowsProp;
    columns: GridColDef[];
    columnGroupingModel?: GridColumnGroupingModel;
}

export default function MembersGridTable({ rows, columns, columnGroupingModel = [] }: GridProps) {
    const memoRows = useMemo(() => rows, [rows]);
    const memoColumns = useMemo(() => columns, [columns]);

    const handelProccess = async (newRow: GridRowModel, oldRow: GridRowModel) => {
        const changedKey = Object.keys(newRow).find(
            (key) => newRow[key] !== oldRow[key]
        );
        if (!changedKey) return oldRow;

        const newValidRow = await toast.promise<GridRowModel>(async () => {

            const changedValue = newRow[changedKey];
            const isAttendance: boolean = Object.values(AttendanceStatus).includes(changedValue);
            const hasExcuse: boolean = changedKey.endsWith("_excuse");

            const { response } = await API.POST(`/organizer/attendance/{track_name}/editor/`, {
                params: { path: { track_name: oldRow.track } },
                body: {
                    code: newRow.code,
                    field: changedKey.replace(hasExcuse ? "_excuse" : "_date", ''),
                    value: hasExcuse ? newRow[changedKey.replace("_excuse", "_date")] : changedValue,
                    type: isAttendance || hasExcuse ? "attendance" : "data",
                    excuse: hasExcuse ? newRow[changedKey] : null
                }
            });

            if (response.ok) {
                return newRow;
            }
            return oldRow;
        },
            {
                loading: "Saving....",
                success: "Saved",
                error: "Couldn't save",
            }
        ).unwrap();
        return newValidRow;
    };

    const colorizeCellsFunction = (params: any) => {
        switch (params.value) {
            case AttendanceStatus.ABSENT:
                return 'bg-[red] text-white';
            case AttendanceStatus.PRESENT:
                return 'bg-green-600 text-white';
            case AttendanceStatus.EXCUSED:
                return 'bg-yellow-300 text-black';
            case MemberStatus.WARNING:
                return 'bg-yellow-300 text-black';
            case MemberStatus.NORMAL:
                return 'bg-blue-600 text-white';
            case MemberStatus.FIRED:
                return 'bg-[red] text-white';
            default:
                return '';
        };
    };

    return (
        <div className='h-[85svh]'>
            <DataGrid
                rows={memoRows}
                columns={memoColumns}
                getCellClassName={colorizeCellsFunction}
                processRowUpdate={handelProccess}
                columnGroupingModel={columnGroupingModel}
                showColumnVerticalBorder
                showCellVerticalBorder
                showToolbar
            />
        </div>
    )
}
