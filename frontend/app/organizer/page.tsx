import serverApi from "../utils/api";
import { Track } from "../utils/api_types_helper";

export default async function OrganizerPage() {
    const res = await serverApi<Track[]>("GET", "/tracks/");
    if (!res.success) {
        console.warn(res.status);
        console.warn(res.data);
        return null;
    }

    return (
        <>
            <h1>OrganizerPage</h1>
            {res?.data?.map((track) => <p key={track.id}>{track.track}</p>)}
        </>
    )
}
