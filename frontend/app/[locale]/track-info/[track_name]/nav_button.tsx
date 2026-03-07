'use client';

import Button from "@mui/material/Button";
import { Link } from "@/i18n/navigation";

export function NavButton() {
    return <Button
        component={Link}
        href="/register"
        variant="contained"
        size="large"
        sx={{
            borderRadius: 3,
            textTransform: 'none',
            fontWeight: 'bold',
            px: 4,
            py: 1.5,
            boxShadow: 'none',
            '&:hover': {
                boxShadow: 'none',
            }
        }}
    >
        Register Now
    </Button>;
}