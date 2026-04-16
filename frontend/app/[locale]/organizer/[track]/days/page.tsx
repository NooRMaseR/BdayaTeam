import { getTranslations } from 'next-intl/server';
import Days from '@/app/components/day_card';
import BodyM from '@/app/components/bodyM';
import API from '@/app/utils/api.server';
import type { Metadata } from 'next';

export async function generateMetadata(): Promise<Metadata> {
    const tr = await getTranslations("trackPage");
    
    return {
        title: tr("days")
    }
}

export default async function DaysPage({ params }: { params: Promise<{ track: string }> }) {
    const { track } = await params;
    const { data } = await API.GET(`/api/organizer/attendance/{track_name}/days/`, {
        params: { path: { track_name: track } },
        next: { revalidate: 300, tags: [`${track}_days`] }
    });

    return (
        <BodyM>
            <Days data={data} track={track} />
        </BodyM>
    )
}
