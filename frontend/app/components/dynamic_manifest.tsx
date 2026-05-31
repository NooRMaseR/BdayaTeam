'use client';

import { useAuthStore } from '../utils/store';

export default function DynamicManifest() {
    const isAuthed = useAuthStore(state => state.isAuthed);
    const user = useAuthStore(state => state.user);
    
    if (!isAuthed || !user) {
        return <link rel="manifest" href="/manifest.json" />
    };

    return (
        <link rel="manifest" href={`/manifest.json?role=${user?.role}&track=${user?.track?.name}`} />
    )
}
