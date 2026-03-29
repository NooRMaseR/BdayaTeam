import TextField, { type TextFieldProps } from "@mui/material/TextField";
import React from "react";

const firstLetterRegex = /[a-zA-Z\u0600-\u06FF]/;
const arabicRegex = /[\u0600-\u06FF]/;

const LocaledTextField = React.forwardRef<HTMLDivElement, TextFieldProps>((props, ref) => {
    const [dir, setDir] = React.useState<"rtl" | "ltr">("ltr");
    const { onChange, ...restProps } = props;

    const handleCharChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const value = e.target.value;
        const firstLetterMatch = value.match(firstLetterRegex);

        if (firstLetterMatch) {
            const firstLetter = firstLetterMatch[0];
            
            if (arabicRegex.test(firstLetter)) {
                setDir("rtl");
            } else {
                setDir("ltr");
            }
        } else if (value.trim() === "") {
            setDir("ltr");
        }

        if (onChange) {
            onChange(e);
        }
    };

    return <TextField {...restProps} dir={dir} onChange={handleCharChange} ref={ref} />;
});

LocaledTextField.displayName = "LocaledTextField";

export default LocaledTextField;