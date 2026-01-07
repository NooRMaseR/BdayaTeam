
export type Track = {
    readonly id: number;
    readonly track: string;
    readonly description?: string | null;
}

export type CreateTrack = Omit<Track, "id"> & {
    readonly prefix: string;
};

export type SendLogIn = {
    readonly email: string;
    readonly password: string;
}

export type GetLogIn = {
    readonly username: string;
    readonly role: "member" | "technical" | "organizer";
    readonly track: Omit<Track, "description"> | null;
}

export type SendRegister = {
    readonly request_track_id: number;
    readonly name: string;
    readonly email: string;
    readonly collage_code: string;
    readonly phone_number: string
}

export enum MemberStatus {
    NORMAL = "normal",
    WARNING = "warning",
    FIRED = "fired",
}

export enum AttendanceStatus {
    PRESENT = "present",
    ABSENT = "absent",
    EXCUSED = "excused",
}

export type AttendanceDay = {
    readonly id: number;
    readonly day: string;
    readonly track: Omit<Track, 'description'>;
}

export type Settings = {
    isRegisterEnabled: boolean;
    organizerCanEdit: string[];
    siteImage: string | null;
}
