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

export type LocaleOptions = 'en' | 'ar';