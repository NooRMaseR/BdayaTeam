import { API } from '@/app/utils/api.server';
import Days from '@/app/components/day_card';

export default async function DaysPage({ params }: { params: Promise<{ track: string }> }) {
    const { track } = await params;
    const {data} = await API.GET(`/api/organizer/attendance/{track_name}/days/`, { params: { path: { track_name: track } } });

    return (
        <Days data={data} track={track} />
    )
}
