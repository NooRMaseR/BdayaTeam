import { getTranslations } from 'next-intl/server';
import type { Metadata } from 'next';
import LogInForm from './form';

export const revalidate = 1000;

export async function generateMetadata(): Promise<Metadata> { 
  const tr = await getTranslations('loginPage');
  
  return {
    title: tr('metaTitle'),
    description: tr('metaDesc'),
    openGraph: {
      title: tr('metaTitle'),
      description: tr('metaDesc'),
      images: ["/favicon.svg"],
    },
  }
}

export default function LoginPage() {
  return <LogInForm />
}
