'use client';

import { prefixer } from 'stylis';
import { useLocale } from 'next-intl';
import createCache from '@emotion/cache';
import { CacheProvider } from '@emotion/react';
import rtlPlugin from '@mui/stylis-plugin-rtl';
import { type ReactNode, useMemo } from 'react';
import { ProgressProvider } from '@bprogress/next/app';
import { createTheme, ThemeProvider } from '@mui/material/styles';


export function LoadingProvider({ children }: { children: React.ReactNode }) {
  return (
    <ProgressProvider
      height="4px" 
      color="blue"
      options={{ showSpinner: false }}
      shallowRouting
    >
      {children}
    </ProgressProvider>
  );
};

export function RegisterThemeProvider({ children }: { children: ReactNode }) {
  const locale = useLocale();
  const isAr = locale === 'ar';
  const cache = useMemo(() => {
    return createCache({
      key: isAr ? 'muirtl' : 'mui',
      stylisPlugins: isAr ? [prefixer, rtlPlugin] : [],
    });
  }, [isAr]);

  const theme = useMemo(() => {
    return createTheme({
      direction: isAr ? 'rtl' : 'ltr',
      typography: {
        fontFamily: isAr ? 'var(--font-arabic), Arial' : 'Arial',
      },
    });
  }, [isAr]);

  return (
    <CacheProvider value={cache}>
      <ThemeProvider theme={theme}>
        {children}
      </ThemeProvider>
    </CacheProvider>
  );
}