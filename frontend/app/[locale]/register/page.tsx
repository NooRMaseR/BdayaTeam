import { fetchSiteImage, serverGraphQL } from '../../utils/api_utils';
import type { SeeCanRegisterQuery } from '../../generated/graphql';
import { CAN_REGISTER } from '../../utils/graphql_helpers';
import { fetchTracks } from '../../utils/api.server';
import { getTranslations } from 'next-intl/server';
import type { Metadata } from 'next';
import RegisterForm from './form';

export async function generateMetadata(): Promise<Metadata> { 
  const [tr, res] = await Promise.all(
    [
      getTranslations('registerPage'),
      fetchSiteImage()
    ]
  );
  const site = res.data.allSettings?.siteImage;

  return {
    title: tr('metaTitle'),
    description: tr('metaDesc'),
    openGraph: {
      title: tr('metaTitle'),
      description: tr('metaDesc'),
      images: site ? [`${process.env.NEXT_PUBLIC_API_URL}${process.env.NEXT_PUBLIC_MEDIA_URL}${site}`] : undefined,
    },
  }
}

export default async function RegisterPage() {
  const [resTracks, canRegister] = await Promise.all(
    [
      fetchTracks(),
      serverGraphQL<SeeCanRegisterQuery>(CAN_REGISTER)
    ]
  );
  
  return <RegisterForm tracks={resTracks.data ?? []} canRegister={canRegister.data.canRegister} />
}

