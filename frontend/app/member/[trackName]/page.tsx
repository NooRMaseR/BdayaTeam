import { Metadata } from 'next';

export const metadata: Metadata = {
    title: "Member Team Bdaya",
    description: "Member Team Bdaya, Come and manage your tasks to get bonus and win a certificate",
    keywords: "Member,member,Tasks,Profile,Task"
}

export default async function MemberTrackPage({ params }: { params: Promise<Record<string, string>> }) {
    const { trackName } = await params;
    return (
        <>
            <h1>Member Track {trackName}</h1>
        </>
    )
}
