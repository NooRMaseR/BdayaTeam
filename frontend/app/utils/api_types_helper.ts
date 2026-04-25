import type { GridColDef, GridColumnGroupingModel, GridRowsProp } from "@mui/x-data-grid"

export enum MemberStatus {
    NORMAL = "normal",
    WARNING1 = "warning 1",
    WARNING2 = "warning 2",
    FIRED = "fired",
}

export enum AttendanceStatus {
    PRESENT = "present",
    ABSENT = "absent",
    EXCUSED = "excused",
}

export type GetMemberGridType = {
    rows: GridRowsProp,
    columns: GridColDef[],
    groupModel: GridColumnGroupingModel
}

export type MemberTaskSend = {
    task_id: number;
    notes?: string;
    files?: string[];
}

export type TrackCreate = {
    name: string;
    prefix: string;
    en_description: string;
    ar_description: string;
    image: string;
}

export type LocaleOptions = 'en' | 'ar';