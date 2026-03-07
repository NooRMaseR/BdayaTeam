"use client";

import { useLocale } from 'next-intl';
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import { usePathname, useRouter } from '@/i18n/navigation';

export default function LanguageSwitcher() {
    const locale = useLocale();
    const pathname = usePathname();
    const router = useRouter();

    const toggleLanguage = (newLocale: string) => router.replace(pathname, { locale: newLocale });

    return (
        <ButtonGroup variant="outlined" size="small" aria-label="language switcher">
            <Button
                onClick={() => toggleLanguage('en')}
                variant={locale === 'en' ? 'contained' : 'outlined'}
                sx={{ color: 'white' }}
            >
                EN
            </Button>
            <Button
                onClick={() => toggleLanguage('ar')}
                variant={locale === 'ar' ? 'contained' : 'outlined'}
                sx={{ color: 'white' }}
            >
                عربي
            </Button>
        </ButtonGroup>
    );
}