'use client';

import React from 'react';
import { useTranslations } from 'next-intl';
import TextField from '@mui/material/TextField';
import IconButton from '@mui/material/IconButton';
import InputAdornment from '@mui/material/InputAdornment';
import VisibilityIcon from '@mui/icons-material/Visibility';
import type { TextFieldProps } from '@mui/material/TextField';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';

const PasswordField = React.forwardRef<HTMLDivElement, TextFieldProps>((props, ref) => {
    const [hidden, setHidden] = React.useState<boolean>(true);
    const handelHidden = () => setHidden((pre) => !pre);
    const tr = useTranslations('loginPage');
    return (
        <TextField
            variant='filled'
            ref={ref}
            type={hidden ? 'password' : "text"}
            autoComplete='current-password'
            slotProps={{
                input: {
                    endAdornment: (
                        <InputAdornment position='end'>
                            <IconButton onClick={handelHidden} sx={{color: "white"}}>
                                {hidden ? <VisibilityIcon /> : <VisibilityOffIcon />}
                            </IconButton>
                        </InputAdornment>
                    )
                }
            }}
            label={tr('password')}
            fullWidth
            required
            sx={{ borderRadius: "0.5rem" }}
            {...props}
        />
    );
});

PasswordField.displayName = 'PasswordField';

export default PasswordField;