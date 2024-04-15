'use client';
import {createTheme} from '@mui/material/styles';


const theme = createTheme({
    palette: {
        mode: 'light',
    },

    components: {
        MuiAlert: {
            styleOverrides: {
                root: ({ownerState}) => ({
                    ...(ownerState.severity === 'info' && {
                        backgroundColor: '#60a5fa',
                    }),
                }),
            },
        },
    },
});

export default theme;
