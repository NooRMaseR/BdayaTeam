import type { SettingsSiteImageQuery } from '@/app/generated/graphql';
import { GET_SITE_IMAGE_SETTINGS } from '@/app/utils/graphql_helpers';
import { serverGraphQL } from '@/app/utils/api_utils';
import { getTranslations } from 'next-intl/server';
import type { Metadata } from 'next';
import LogInForm from './form';

export async function generateMetadata(): Promise<Metadata> { 
  const [tr, res] = await Promise.all(
    [
      getTranslations('loginPage'),
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

export default function LoginPage() {
  return (
    <LogInForm />
  )
}
