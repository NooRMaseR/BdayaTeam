'use client';

import { prefixer } from 'stylis';
import { useLocale } from 'next-intl';
import createCache from '@emotion/cache';
import { CacheProvider } from '@emotion/react';
import rtlPlugin from '@mui/stylis-plugin-rtl';
import React, { type ReactNode, useMemo } from 'react';
import { ProgressProvider } from '@bprogress/next/app';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { ThemeProvider as NextThemeProvider, useTheme, type ThemeProviderProps } from 'next-themes';
import { CssBaseline } from '@mui/material';


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
  
  const { resolvedTheme } = useTheme(); 
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  const cache = useMemo(() => {
    return createCache({
      key: isAr ? 'muirtl' : 'mui',
      stylisPlugins: isAr ? [prefixer, rtlPlugin] : [],
    });
  }, [isAr]);

  const theme = useMemo(() => {
    return createTheme({
      direction: isAr ? 'rtl' : 'ltr',
      
      palette: {
        mode: resolvedTheme === 'dark' ? 'dark' : 'light',
      },
      
      typography: {
        fontFamily: isAr ? 'var(--font-arabic), Arial' : 'Arial',
      },
    });
  }, [isAr, resolvedTheme]);

  if (!mounted) {
    return <div style={{ visibility: 'hidden' }}>{children}</div>;
  }

  return (
    <CacheProvider value={cache}>
      <ThemeProvider theme={theme}>
        <CssBaseline /> 
        {children}
      </ThemeProvider>
    </CacheProvider>
  );
}

export function RegisterNextThemeProvider({ children, ...props }: ThemeProviderProps) {
  return <NextThemeProvider {...props}>{ children }</NextThemeProvider>
}