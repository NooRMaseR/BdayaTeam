'use client';

import { IconButton, InputAdornment, TextField, TextFieldProps } from '@mui/material';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import VisibilityIcon from '@mui/icons-material/Visibility';
import React from 'react';

const PasswordField = React.forwardRef<HTMLDivElement, TextFieldProps>((props, ref) => {
    const [hidden, setHidden] = React.useState<boolean>(true);
    const handelHidden = () => setHidden((pre) => !pre);

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
                            <IconButton onClick={handelHidden}>
                                {hidden ? <VisibilityIcon /> : <VisibilityOffIcon />}
                            </IconButton>
                        </InputAdornment>
                    )
                }
            }}
            label="password"
            fullWidth
            required
            sx={{ bgcolor: "whitesmoke", borderRadius: "0.5rem" }}
            {...props}
        />
    );
});

export default PasswordField;