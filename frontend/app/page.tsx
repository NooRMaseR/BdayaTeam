import Image from 'next/image';
import serverApi from './utils/api';
import { Track } from './utils/api_types_helper';
import NavButtons from './components/home/nav_buttons';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';
import { Button, Container, Typography, Card, CardContent, Chip } from '@mui/material';

export default async function HomePage() {
  const years = new Date().getFullYear() - 2015;
  const res = await serverApi<Track[]>("GET", "/tracks/");

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">

      <section className="relative bg-linear-to-br from-blue-700 to-indigo-900 text-white py-24 px-4 overflow-hidden">
        <Container maxWidth="lg" className="relative z-10 text-center">
          <Chip
            label={`${years} Years of Excellence`}
            color="secondary"
            className="mb-6 font-bold uppercase tracking-wider"
            icon={<VerifiedUserIcon />}
          />

          <h1 className="text-4xl md:text-6xl font-extrabold mb-6 leading-tight">
            Empowering the Next Generation of <br />
            <span className="text-blue-300">Team Bdaya</span>
          </h1>

          <p className="text-lg md:text-xl text-blue-100 max-w-2xl mx-auto mb-10">
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
            {res.data?.map((track) => (
              <TrackCard
                title={track.track}
                desc={track.description || ""}
                key={track.id}
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
              Team Bdaya wasn't built in a boardroom. It started {years} years ago with a simple mission: to bridge the gap between academic theory and real-world application.
            </p>
            <p className="text-gray-600 text-lg leading-relaxed">
              We believe education should be accessible to everyone. That's why all our tracks, from Graphic Design to Software Engineering, remain 100% free.
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

function TrackCard({ title, desc }: { title: string, desc: string }) {
  return (
    <Card className="hover:shadow-xl transition-shadow duration-300 border-t-4 border-transparent hover:border-blue-500 hover:scale-110 cursor-default" sx={{ transition: "scale ease-out 300ms, border-color ease-out 300ms;", width: "20rem", height: "10rem" }}>
      <CardContent className="flex flex-col items-center text-center p-8">
        <h3 className="text-xl font-bold text-gray-800 mb-2">{title}</h3>
        <p className="text-gray-600 text-sm leading-relaxed line-clamp-3 overflow-hidden">
          {desc}
        </p>
      </CardContent>
    </Card>
  )
}