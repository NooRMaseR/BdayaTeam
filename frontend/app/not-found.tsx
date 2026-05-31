import Link from "next/link";
import Image from "next/image";

export default function NotFound() {
  return (
    <html>
      <body
        style={{
          margin: 0,
          backgroundColor: '#121212',
          color: '#ffffff',
          fontFamily: 'system-ui, sans-serif'
        }}
      >
        <div style={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          padding: '20px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'center', margin: '16px 0' }}>
            <Image
              src="/idk.gif"
              alt="404 Page animation"
              width={300}
              height={300}
              style={{borderRadius: '1rem'}}
              unoptimized
            />
          </div>
          <h1 style={{ fontSize: '8rem', margin: 0, fontWeight: 900, lineHeight: 1 }}>404</h1>
          <h2 style={{ fontSize: '2rem', margin: '10px 0' }}>Page Not Found</h2>
          <p style={{ fontSize: '1.1rem', color: '#a1a1aa', marginBottom: '40px', maxWidth: '400px' }}>
            We searched everywhere, but it seems this page has gone missing.
          </p>
          <Link
            href="/"
            style={{
              padding: '14px 32px',
              backgroundColor: '#ffffff',
              color: '#000000',
              textDecoration: 'none',
              borderRadius: '50px',
              fontWeight: 700
            }}
          >
            Back to Home
          </Link>
        </div>
      </body>
    </html>
  );
}