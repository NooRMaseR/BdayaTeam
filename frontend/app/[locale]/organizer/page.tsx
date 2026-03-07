import NavigationCard from "../../components/navigation_card";
import { fetchSiteImage } from "../../utils/api_utils";
import { fetchTracks } from "../../utils/api.server";
import { getTranslations } from "next-intl/server";
import BodyM from "@/app/components/bodyM";
import type { Metadata } from "next";
import ResetAll from "./reset_all";

export const revalidate = 300;

export async function generateMetadata(): Promise<Metadata> {
    const [tr, res] = await Promise.all(
        [
            getTranslations('organizerPage'),
            fetchSiteImage()
        ]
    );
    const site = res.data.allSettings?.siteImage;

    return {
        title: tr('metaTitle'),
        description: tr('metaDesc'),
        keywords: tr('metaKeys'),
        openGraph: {
            title: tr('metaTitle'),
            description: tr("metaDesc"),
            images: site ? [`${process.env.NEXT_PUBLIC_MEDIA_URL}${site}`] : undefined,
        },
    }
}

export default async function OrganizerPage({params}: {params: Promise<{locale: string}>}) {
    const [tr, tracks, {locale}] = await Promise.all(
        [
            getTranslations('organizerPage'),
            fetchTracks(),
            params
        ]
    );

    return (
        <BodyM>
            <div className="flex justify-center flex-wrap w-full gap-10">
                {tracks.data?.map((track) => (
                    <NavigationCard
                        url={`organizer/${track.name}`}
                        title={track.name}
                        desc={locale === "ar" ? track.ar_description : track.en_description}
                        imageUrl={track.image ? `${process.env.NEXT_PUBLIC_MEDIA_URL}/${track.image}` : undefined}
                        key={track.id}
                    />
                ))}
                <NavigationCard
                    url="organizer/add-track"
                    title={tr('add')}
                    desc={tr('add')}
                />
                <NavigationCard
                    url="organizer/settings"
                    title={tr('settings')}
                    desc={tr('settingsDesc')}
                />
                <NavigationCard
                    url={`${process.env.NEXT_PUBLIC_API_URL}/api/admin/`}
                    title={tr('admin')}
                    desc={tr('adminDesc')}
                />
                <ResetAll />
            </div>
        </BodyM>
    )
}
