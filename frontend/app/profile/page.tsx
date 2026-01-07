import { API } from '../utils/api.server';
import { Box, Chip } from '@mui/material';

function Stat({ label, value }: { label: string; value: number | string }) {
    return (
        <div className="flex-1 bg-slate-50 p-3 rounded-lg text-center">
            <div className="text-lg font-semibold text-slate-900">{value}</div>
            <div className="mt-1 text-xs text-slate-500">{label}</div>
        </div>
    )
}

export default async function ProfilePage() {
    const {response, data} = await API.GET("/member/profile/{member_code}/", {params: {path: {member_code: "p-1"}}});
    const user = response.ok && data ? data : null;

    if (!user) {
        return (
            <main className="min-h-screen flex items-center justify-center p-8 bg-linear-to-br from-sky-50 via-emerald-50 to-rose-50">
                <div className="w-full max-w-3xl bg-white/60 backdrop-blur-sm border border-slate-100/50 rounded-xl p-8 shadow-lg">
                    <h2 className="text-xl font-semibold text-slate-900">Profile</h2>
                    <p className="mt-3 text-slate-500">Unable to load profile.</p>
                </div>
            </main>
        )
    }

    return (
        <main className="min-h-screen flex justify-center w-full bg-linear-to-br from-blue-400 via-green-400 to-rose-50">
            <section className="w-full bg-white/70 backdrop-blur-sm rounded-xl shadow-md border-slate-100/50">
                <Box component={"div"} className="flex items-center gap-4 mb-4 p-4 bg-blue-300" sx={{height: "10rem"}}>
                    <div className="w-18 h-18 flex items-center justify-center rounded-full bg-linear-to-br from-sky-500 to-emerald-400 text-white font-bold text-2xl">
                        {user.name[0].toUpperCase()}
                    </div>
                    <div>
                        <h1 className="text-2xl font-semibold text-slate-900">{user.name}</h1>
                        <Chip label={`Track: ${user.track.track}`} color='info' sx={{mr: "1rem"}} />
                        <Chip label={`Code: ${user.code}`} color='info' />
                    </div>
                </Box>

                <div className="flex gap-3 mt-4 flex-col p-4 sm:flex-row">
                    <Stat label="Absents" value={user.absents} />
                    <Stat label="Tasks Sent" value={user.total_tasks_sent} />
                    <Stat label="Missing Tasks" value={user.missing_tasks} />
                </div>
            </section>
        </main>
    )
}
