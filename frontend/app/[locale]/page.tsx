import Image from 'next/image';
import type { Metadata } from 'next';
import Chip from '@mui/material/Chip';
import { API } from '../utils/api.server';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import NavButtons from '../components/nav_buttons';
import { serverGraphQL } from '../utils/api_utils';
import { getTranslations } from 'next-intl/server';
import NormalAnimation from '../components/animations';
import NavigationCard from '../components/navigation_card';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';
import type { SettingsHeroImageQuery, SettingsSiteImageQuery } from '../generated/graphql';
import { GET_HERO_IMAGE_SETTINGS, GET_SITE_IMAGE_SETTINGS } from '../utils/graphql_helpers';

export async function generateMetadata(): Promise<Metadata> { 
  const [tr, res] = await Promise.all(
    [
      getTranslations('homePage'),
      serverGraphQL<SettingsSiteImageQuery>(GET_SITE_IMAGE_SETTINGS)
    ]
  );
  const site = res.data.allSettings?.siteImage;

  return {
    title: tr('metaTitle'),
    description: tr('metaDesc'),
    keywords: tr('metaKeys'),
    openGraph: {
      title: tr('metaTitle'),
      description: tr('metaDesc'),
      images: site ? [`${process.env.NEXT_PUBLIC_API_URL}${process.env.NEXT_PUBLIC_MEDIA_URL}${site}`] : undefined,
    },
  }
}

export default async function HomePage({params}: {params: Promise<{locale: string}>}) {
  const years = new Date().getFullYear() - 2015;
  const [ paramsPrmise, tr, tracks, hero ] = await Promise.all(
    [
      params,
      getTranslations('homePage'),
      API.GET("/api/tracks/"),
      serverGraphQL<SettingsHeroImageQuery>(GET_HERO_IMAGE_SETTINGS)
    ]
  );
  
  const { locale } = paramsPrmise;

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <NormalAnimation
        component='section'
        className='relative bg-sky-500 py-24 overflow-hidden aspect-16/10'
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ ease: 'easeOut' }}>
        {
          hero.success && hero.data.allSettings?.heroImage
            ? <Image src={`${process.env.NEXT_PUBLIC_MEDIA_URL}${hero.data.allSettings?.heroImage}`} alt='Team pic' fill priority style={{ objectFit: "cover" }} unoptimized />
            : null
        }
      </NormalAnimation>

      <section className={`relative bg-blue-700 text-white py-8 px-4 overflow-hidden`}>
        <Container maxWidth="lg" className="relative z-10 text-center">
          <Chip
            label={tr('excellence', { years })}
            color="secondary"
            className="mb-6 font-bold uppercase tracking-wider"
            icon={<VerifiedUserIcon />}
          />

          <h1 className="text-4xl md:text-6xl font-extrabold mb-6 leading-tight">
            {tr('nextGen')} <br />
            <span className="text-blue-300">{tr('teamBdaya')}</span>
          </h1>

          <p className="text-lg md:text-xl max-w-2xl mx-auto mb-10">
            {tr('join')} <strong>{tr('teamBdaya')}</strong>. {tr('weProvide')}
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <NavButtons locale={locale} />
          </div>
        </Container>
      </section>


      <section className="bg-white py-10 shadow-sm border-b border-gray-100">
        <Container maxWidth="lg">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center divide-x divide-gray-100">
            <StatItem number={`${years - 1}+`} label={tr('exp')} />
            <StatItem number="15k+" label={tr('std')} />
            <StatItem number="100%" label={tr('freeC')} />
            <StatItem number="24/7" label={tr('support')} />
          </div>
        </Container>
      </section>


      <section className="py-20">
        <Container maxWidth="lg">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-800 mb-4">{ tr('avlTracks') }</h2>
            <div className="w-20 h-1 bg-blue-600 mx-auto rounded"></div>
          </div>

          <div className="flex justify-center flex-wrap gap-6">
            {tracks.data?.map((track) => (
              <NavigationCard
                title={track.track}
                desc={track.description || ""}
                key={track.id}
                imageUrl={`${process.env.NEXT_PUBLIC_MEDIA_URL}${track.image}`}
              />
            ))}
          </div>
        </Container>
      </section>


      <section className="bg-gray-100 py-20">
        <Container maxWidth="lg" className="flex flex-col md:flex-row items-center gap-12">
          <div className="flex-1">
            <Image
              src="https://images.unsplash.com/photo-1522071820081-009f0129c71c?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
              alt="Team Collaboration"
              className="rounded-2xl shadow-2xl"
              width={700}
              height={700}
            />
          </div>
          <div className="flex-1 space-y-8">
            <Typography variant="overline" className="text-blue-600 font-bold tracking-widest">
              {tr('who')}
            </Typography>
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900">
              {tr('by')}, <br /> {tr('for')}.
            </h2>
            <p className="text-gray-600 text-lg leading-relaxed">
              {tr('bdayaStarted', {years})}
            </p>
            <p className="text-gray-600 text-lg leading-relaxed">
              {tr('weBelieve')}
            </p>
          </div>
        </Container>
      </section>


      <footer className="bg-gray-900 text-gray-400 py-12 border-t border-gray-800">
        <Container maxWidth="lg" className="text-center">
          <p>&copy; {new Date().getFullYear()} {tr('teamBdaya')}. {tr('rights')}.</p>
          <p className="text-sm mt-2">{tr('empowring')}</p>
        </Container>
      </footer>
    </div>
  );
}


function StatItem({ number, label }: { number: string, label: string }) {
  return (
    <div className="p-4">
      <div className="text-3xl md:text-4xl font-bold text-blue-600 mb-1">{number}</div>
      <div className="text-sm text-gray-500 uppercase tracking-wide font-medium">{label}</div>
    </div>
  )
}
