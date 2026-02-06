/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import type { GridRowModel, GridColDef, GridColumnGroupingModel, GridCellParams } from '@mui/x-data-grid';
import { AttendanceStatus, MemberStatus } from '../utils/api_types_helper';
import type { GridRowsProp } from '@mui/x-data-grid';
import { useTranslations } from 'next-intl';
import { DataGrid } from '@mui/x-data-grid';
import { API } from '../utils/api.client';
import { Link } from '@/i18n/navigation';
import { Button } from '@mui/material';
import { useMemo } from 'react';
import { toast } from 'sonner';

type GridProps = {
    rows: GridRowsProp;
    columns: GridColDef[];
    columnGroupingModel?: GridColumnGroupingModel;
    track: string;
}

export default function MembersGridTable({ rows, columns, columnGroupingModel = [], track }: GridProps) {
    const tr = useTranslations('showMembersPage');
    const memoRows = useMemo(() => rows, [rows]);
    const memoColumns = useMemo<GridColDef[]>(() => [{
        align: "center",
        headerAlign: "center",
        field: "actions",
        headerName: tr("actions"),
        width: 120,
        filterable: false,
        sortable: false,
        renderCell(params) {
            return <Link href={`/profile/${params.id}`}>
                <Button variant='contained'>{tr('profile')}</Button>
            </Link>
        },
    }, ...columns], [columns, tr]);

    const handelProccess = async (newRow: GridRowModel, oldRow: GridRowModel) => {
        const changedKey = Object.keys(newRow).find(
            (key) => newRow[key] !== oldRow[key]
        );
        if (!changedKey) return oldRow;

        const newValidRow = await toast.promise<GridRowModel>(async () => {

            const changedValue = newRow[changedKey];
            const isAttendance: boolean = Object.values(AttendanceStatus).includes(changedValue);
            const hasExcuse: boolean = changedKey.endsWith("_excuse");

            const { response } = await API.POST(`/api/organizer/attendance/{track_name}/editor/`, {
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
                loading: tr('saving'),
                success: tr('saved'),
                error: tr('notSaved'),
            }
        ).unwrap();
        return newValidRow;
    };

    const colorizeCellsFunction = (params: GridCellParams<any, AttendanceStatus | MemberStatus>) => {
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
                label={tr('trackHead', {track})}
                getCellClassName={colorizeCellsFunction}
                processRowUpdate={handelProccess}
                columnGroupingModel={columnGroupingModel}
                showColumnVerticalBorder
                showCellVerticalBorder
                showToolbar
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
            />
        </div>
    )
}
