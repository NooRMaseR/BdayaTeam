import type { SeeCanRegisterQuery, SettingsSiteImageQuery } from '../../generated/graphql';
import { CAN_REGISTER, GET_SITE_IMAGE_SETTINGS } from '../../utils/graphql_helpers';
import { serverGraphQL } from '../../utils/api_utils';
import { getTranslations } from 'next-intl/server';
import { API } from '../../utils/api.server';
import type { Metadata } from 'next';
import RegisterForm from './form';

export async function generateMetadata(): Promise<Metadata> { 
  const [tr, res] = await Promise.all(
    [
      getTranslations('registerPage'),
      serverGraphQL<SettingsSiteImageQuery>(GET_SITE_IMAGE_SETTINGS)
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
      API.GET("/api/tracks/", { next: { revalidate: 300 } }),
      serverGraphQL<SeeCanRegisterQuery>(CAN_REGISTER)
    ]
  );

  if (resTracks.response.ok) {
    return <RegisterForm tracks={resTracks.data || []} canRegister={canRegister.data.canRegister} />
  }
  return <RegisterForm tracks={[]} canRegister={false} />
}

