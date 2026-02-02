import Image from 'next/image';
import type { Metadata } from 'next';
import { API } from './utils/api.server';
import NavButtons from './components/nav_buttons';
import { serverGraphQL } from './utils/api_utils';
import NormalAnimation from './components/animations';
import NavigationCard from './components/navigation_card';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';
import { Button, Container, Typography, Chip } from '@mui/material';
import type { SettingsHeroImageQuery, SettingsSiteImageQuery } from './generated/graphql';
import { GET_HERO_IMAGE_SETTINGS, GET_SITE_IMAGE_SETTINGS } from './utils/graphql_helpers';

export async function generateMetadata(): Promise<Metadata> { 
  const res = await serverGraphQL<SettingsSiteImageQuery>(GET_SITE_IMAGE_SETTINGS);
  const site = res.data.allSettings?.siteImage;

  return {
    title: "Team Bdaya Home",
    description: "Welcome To Team Bdaya, A Place where you can build skills and get courses for free",
    keywords: "Join, Team, Bdaya, free, Tracks",
    openGraph: {
      title: `Team Bdaya Home`,
      description: `Welcome To Team Bdaya, A Place where you can build skills and get courses for free`,
      images: site ? [`${process.env.NEXT_PUBLIC_MEDIA_URL}${site}`] : undefined,
    },
  }
}

export default async function HomePage() {
  const years = new Date().getFullYear() - 2015;
  const [ tracks, hero ] = await Promise.all(
    [
      API.GET("/api/tracks/"),
      serverGraphQL<SettingsHeroImageQuery>(GET_HERO_IMAGE_SETTINGS)
    ]
  );

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <NormalAnimation
        component='section'
        className='relative bg-sky-500 py-24 overflow-hidden h-120'
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
            label={`${years} Years of Excellence`}
            color="secondary"
            className="mb-6 font-bold uppercase tracking-wider"
            icon={<VerifiedUserIcon />}
          />

          <h1 className="text-4xl md:text-6xl font-extrabold mb-6 leading-tight">
            the Next Generation of <br />
            <span className="text-blue-300">Team Bdaya</span>
          </h1>

          <p className="text-lg md:text-xl max-w-2xl mx-auto mb-10">
            Join <strong>Team Bdaya</strong>. We provide premium, free education in programming and design.
            Start your journey today and master the skills of tomorrow.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <NavButtons />
          </div>
        </Container>
      </section>


      <section className="bg-white py-10 shadow-sm border-b border-gray-100">
        <Container maxWidth="lg">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center divide-x divide-gray-100">
            <StatItem number={`${years - 1}+`} label="Years Experience" />
            <StatItem number="15k+" label="Students Taught" />
            <StatItem number="100%" label="Free Courses" />
            <StatItem number="24/7" label="Mentor Support" />
          </div>
        </Container>
      </section>


      <section className="py-20">
        <Container maxWidth="lg">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-800 mb-4">Our Core Tracks</h2>
            <div className="w-20 h-1 bg-blue-600 mx-auto rounded"></div>
            <p className="text-gray-600 mt-4">Master industry-standard technologies with our tailored roadmaps.</p>
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
          <div className="flex-1 space-y-6">
            <Typography variant="overline" className="text-blue-600 font-bold tracking-widest">
              Who We Are
            </Typography>
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900">
              Built by Students, <br /> For Students.
            </h2>
            <p className="text-gray-600 text-lg leading-relaxed">
              Team Bdaya wasn&apos;t built in a boardroom. It started {years} years ago with a simple mission: to bridge the gap between academic theory and real-world application.
            </p>
            <p className="text-gray-600 text-lg leading-relaxed">
              We believe education should be accessible to everyone. That&apos;s why all our tracks, from Graphic Design to Software Engineering, remain 100% free.
            </p>
            <Button variant="text" color="primary" className="font-bold text-lg p-0 hover:bg-transparent">
              Read Our Story &rarr;
            </Button>
          </div>
        </Container>
      </section>


      <footer className="bg-gray-900 text-gray-400 py-12 border-t border-gray-800">
        <Container maxWidth="lg" className="text-center">
          <p>&copy; {new Date().getFullYear()} Team Bdaya. All rights reserved.</p>
          <p className="text-sm mt-2">Empowering Minds Since 2015.</p>
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
