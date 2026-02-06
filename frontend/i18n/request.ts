import {getRequestConfig} from 'next-intl/server';

export default getRequestConfig(async (params) => {
  const locale = await params.requestLocale || 'en';
  const messages = (await import(`../messages/${locale}.json`)).default
  return {
    locale,
    messages
  }
});