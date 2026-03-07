import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Paper from '@mui/material/Paper';
import Box from '@mui/material/Box';

import type { Get_Track_ImageQuery } from '@/app/generated/graphql';
import { GET_TRACK_IMAGE } from '@/app/utils/graphql_helpers';
import { serverGraphQL } from '@/app/utils/api_utils';
import BodyM from '@/app/components/bodyM';
import { NavButton } from './nav_button';
import API from '@/app/utils/api.server';
import type { Metadata } from 'next';
import Image from 'next/image';

type Props = {params: Promise<{ track_name: string, locale: 'en' | "ar" }>}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { track_name } = await params;
  const readableTrack = track_name.replaceAll("%20", ' ');

  const trackRes = await serverGraphQL<Get_Track_ImageQuery>(GET_TRACK_IMAGE, { track: readableTrack });
  let imageUrl: string | undefined;
  if (trackRes.success) {
    imageUrl = `${process.env.NEXT_PUBLIC_MEDIA_URL}${trackRes.data.track?.image}`;
  }

  return {
    title: `${readableTrack} Info`,
    description: `Check out Track ${readableTrack} Info`,
    
    openGraph: {
      title: `${readableTrack} Info`,
      description: `Check out Track ${readableTrack} Info`,
      images: imageUrl ? [imageUrl] : undefined, 
    },
  };
}


export default async function TrackHero({ params }: Props ) {
    const { track_name, locale } = await params;
    const readableTrackName = track_name.replaceAll("%20", ' ');
    const { data } = await API.GET(`/api/tracks/{track_name}/`, {params: {path: {track_name: readableTrackName}}});

    if (!data) {
        return <Typography>No track Found</Typography>
    }

    return (
        <BodyM>
            <Container maxWidth="lg" sx={{ mt: 4, mb: 6 }}>
                <Paper
                    elevation={0}
                    sx={{
                        position: 'relative',
                        overflow: 'hidden',
                        borderRadius: 6,
                        bgcolor: 'background.paper',
                        border: '1px solid',
                        borderColor: 'divider',
                        display: 'flex',
                        flexDirection: { xs: 'column', md: 'row' },
                        minHeight: 300,
                    }}
                >
                    {/* Track Image Section */}
                    <Box sx={{ position: 'relative', width: { xs: '100%', md: '40%' }, height: { xs: 200, md: 'auto' } }}>
                        <Image
                            src={`${process.env.NEXT_PUBLIC_API_URL}${data.image}`}
                            alt={data.name}
                            fill
                            style={{ objectFit: 'contain' }}
                            priority
                            unoptimized
                        />
                    </Box>
                    {/* Track Text Section */}
                    <Box sx={{ p: { xs: 3, md: 5 }, width: { xs: '100%', md: '60%' }, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                        <Typography
                            variant="overline"
                            color="primary"
                            fontWeight="bold"
                            sx={{ letterSpacing: 2 }}
                        >
                            Selected Track
                        </Typography>
                        <Typography
                            variant="h3"
                            component="h1"
                            fontWeight="800"
                            gutterBottom
                            sx={{ fontSize: { xs: '2rem', md: '3rem' } }}
                        >
                            {readableTrackName}
                        </Typography>
                        <Typography
                            variant="body1"
                            color="text.secondary"
                            sx={{ maxWidth: 500, lineHeight: 1.7 }}
                        >
                            {locale === "ar" ? data.ar_description : data.en_description}
                        </Typography>

                        {/* Navigation Button */}
                        <NavButton />
                    </Box>
                </Paper>
            </Container>
        </BodyM>
    );
}