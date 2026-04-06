import createIntlMiddleware from 'next-intl/middleware';
import { NextResponse, type NextRequest } from 'next/server';

const intlMiddleware = createIntlMiddleware({
  locales: ['en', 'ar'],
  defaultLocale: 'en'
});

export default function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // 1. Run i18n Middleware FIRST
  const response = intlMiddleware(request);

  // 2. Check for Token
  const token = request.cookies.get('refresh_token')?.value;

  // 3. Define Protected Routes
  const isProtectedRoute =
    pathname.includes('/profile') ||
    pathname.includes('/technical') ||
    pathname.includes('/member') ||
    pathname.includes('/organizer');

  // 4. Handle Auth Redirect
  if (isProtectedRoute && !token) {
    const locale = pathname.split('/')[1];
    const targetLocale = ['en', 'ar'].includes(locale) ? locale : 'en';
    
    return NextResponse.redirect(new URL(`/${targetLocale}/login`, request.url));
  }

  return response;
}

export const config = {
  matcher: ['/((?!api|_next|.*\\..*).*)']
};