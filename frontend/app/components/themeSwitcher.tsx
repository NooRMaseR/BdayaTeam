'use client';

import { useTheme } from 'next-themes';
import Tooltip from '@mui/material/Tooltip';
import IconButton from '@mui/material/IconButton';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LightModeIcon from '@mui/icons-material/LightMode';

export default function ThemeSwitcher() {
    const { theme, setTheme } = useTheme();
    const isDarkMode = theme === "dark";
    const toggleMode = () => setTheme(theme === "dark" ? "light" : "dark");
    
    return (
        <Tooltip title={isDarkMode ? "Enable Light Mode" : "Enable Dark Mode"}>
            <IconButton onClick={toggleMode}>
                {isDarkMode ? <DarkModeIcon sx={{color: 'white'}} /> : <LightModeIcon sx={{color: 'white'}} />}
            </IconButton>
        </Tooltip>
    )
}
