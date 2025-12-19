
export type Track = {
    readonly id: number,
    readonly track: string
    readonly description: string | null
}

export type SendLogIn = {
    readonly email: string,
    readonly password: string,
}

export enum UserRole {
    MEMBER = "member",
    TECHNICAL = "technical",
    ORGANIZER = "organizer"
}

export type GetLogIn = {
    readonly username: string,
    readonly role: UserRole,
    readonly track: Track | null
}

export type SendRegister = {
    readonly request_track_id: number,
    readonly name: string,
    readonly email: string,
    readonly collage_code: string,
    readonly phone_number: string
}

export type GetRegister = Omit<SendRegister, "request_track_id"> & {
    readonly code: string
}

export type UserProfile = {
    readonly name: string,
    readonly code: string,
    readonly track: Track,
    readonly absents: number,
    readonly total_tasks_sent: number,
    readonly missing_tasks: number
}