'use client';

import { ProgressProvider } from '@bprogress/next/app';

export default function LoadingProvider({ children }: { children: React.ReactNode }) {
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
