'use client';

import { prefixer } from 'stylis';
import { useLocale } from 'next-intl';
import { Provider } from 'react-redux';
import createCache from '@emotion/cache';
import { CacheProvider } from '@emotion/react';
import rtlPlugin from '@mui/stylis-plugin-rtl';
import { makeStore, AppStore } from '../utils/store';
import { ProgressProvider } from '@bprogress/next/app';
import { type ReactNode, useMemo, useRef } from 'react';
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


export function StoreProvider({ children }: { children: React.ReactNode }) {
  const storeRef = useRef<AppStore>(undefined);
  if (!storeRef.current) {
    storeRef.current = makeStore();
  }
  return <Provider store={ storeRef.current }> { children } </Provider>
}

export function RegisterThemeProvider({ children }: { children: ReactNode }) {
  const locale = useLocale();
  const isAr = locale === 'ar';
  const cache = useMemo(() => {
    return createCache({
      key: isAr ? 'muirtl' : 'mui',
      stylisPlugins: isAr ? [prefixer, rtlPlugin] : [],
    });
  }, [isAr]);

  // 2. Create the Theme
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