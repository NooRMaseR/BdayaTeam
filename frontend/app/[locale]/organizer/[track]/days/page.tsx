import Days from '@/app/components/day_card';
import BodyM from '@/app/components/bodyM';
import API from '@/app/utils/api.server';

export default async function DaysPage({ params }: { params: Promise<{ track: string }> }) {
    const { track } = await params;
    const { data } = await API.GET(`/api/organizer/attendance/{track_name}/days/`, {
        params: { path: { track_name: track } },
        next: { revalidate: 300 }
    });

    return (
        <BodyM>
            <Days data={data} track={track} />
        </BodyM>
    )
}
