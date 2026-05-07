'use client';

import ClickSpark from '@/components/ClickSpark';
import { useTheme } from 'next-themes';
import React from 'react';

export default function ClickSparkWrapper({ children }: { children: React.ReactNode }) {
    const { resolvedTheme } = useTheme();
    const [mounted, setMounted] = React.useState<boolean>(false);

    React.useEffect(() => {
        setMounted(true);
    }, []);
    const currentColor = mounted && resolvedTheme === 'dark' ? '#ffffff' : '#292929';

    return (
        <ClickSpark sparkColor={currentColor} sparkSize={10} sparkRadius={15} sparkCount={8} duration={400}>
            {children}
        </ClickSpark>
    )
}
