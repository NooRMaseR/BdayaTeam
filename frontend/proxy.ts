import createIntlMiddleware from 'next-intl/middleware';
import { NextResponse, type NextRequest } from 'next/server';

const intlMiddleware = createIntlMiddleware({
  locales: ['en', 'ar'],
  defaultLocale: 'en'
});

export default function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // 1. Run i18n Middleware FIRST
  // We capture the response here because it contains the locale headers/cookies
  const response = intlMiddleware(request);

  // 2. Check for Token
  const token = request.cookies.get('refresh_token')?.value;

  // 3. Define Protected Routes
  // Use .includes() to match both "/profile" and "/en/profile" and "/ar/profile"
  const isProtectedRoute =
    pathname.includes('/profile') ||
    pathname.includes('/technical') ||
    pathname.includes('/member') ||
    pathname.includes('/organizer');

  // 4. Handle Auth Redirect
  if (isProtectedRoute && !token) {
    // We need to redirect to the localized login page (e.g., /en/login or /ar/login)
    // We can guess the locale from the URL, or default to 'en'
    const locale = pathname.split('/')[1];
    const targetLocale = ['en', 'ar'].includes(locale) ? locale : 'en';
    
    return NextResponse.redirect(new URL(`/${targetLocale}/login`, request.url));
  }

  // 5. CRITICAL: Return the response created by intlMiddleware
  // If you return NextResponse.next() here, you lose the locale info!
  return response;
}

export const config = {
  // Match everything except static files and APIs
  matcher: ['/((?!api|_next|.*\\..*).*)']
};