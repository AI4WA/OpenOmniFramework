'use client'
import React, {useState} from 'react';

import Header from '@/components/Header'; // Ensure the path to your Header component is correct
import axios, {AxiosError} from 'axios'; // Make sure AxiosError is imported if you're using axios

import {
    Divider,
    Grid,
    Container,
    Box,
    TextField,
    Button,
    Typography,
    Alert,
    Paper,
    List,
    ListItem,
    ListItemAvatar,
    Avatar,
    ListItemText
} from '@mui/material';

import {useAppSelector} from "@/store";
import {useSubscription, gql} from "@apollo/client";
import apiClient from "@/cloud/apiClient";

import VpnKeyIcon from '@mui/icons-material/VpnKey'; // For token actions
import PasswordIcon from '@mui/icons-material/Password'; // For password reset

import isAuth from "@/app/isAuth";
import PersonIcon from '@mui/icons-material/Person'; // For the name
import EmailIcon from '@mui/icons-material/Email'; // Example if y

const USER_TOKEN = gql`
subscription UserToken($userId: bigint!) {
  authtoken_token(where: {user_id: {_eq: $userId}}) {
    key
  }
}
`

const ProfilePage = () => {
        // const router = useRouter();
        const [newPassword, setNewPassword] = useState('');
        const [currentPassword, setCurrentPassword] = useState('');
        const username = useAppSelector(state => state.auth.authState?.username);
        const firstName = useAppSelector(state => state.auth.authState?.firstName);
        const lastName = useAppSelector(state => state.auth.authState?.lastName);
        const userId = useAppSelector(state => state.auth.authState?.userId);
        const [errorMessage, setErrorMessage] = useState('');
        const [successMessage, setSuccessMessage] = useState('');
        const {data} = useSubscription(USER_TOKEN, {
            variables: {userId}
        });

        const handleGenerateToken = async () => {
            // Implement the logic to generate a new token
            try {
                const response = await apiClient.post('/authenticate/api/token/obtain/', {});
            } catch (e) {
                console.log(e);
            }

        };

        const handleResetPassword = async () => {
            // Implement the logic to reset the password
            setErrorMessage("")
            setSuccessMessage("")
            if (newPassword && currentPassword) {
                try {
                    const res = await apiClient.post('/authenticate/api/update_password/', {
                        old_password: currentPassword,
                        new_password: newPassword
                    });
                    console.log(res.data)

                    if (res.status === 200) {
                        // Show a success message or handle the state update
                        setSuccessMessage("Password updated successfully")
                    } else {
                        setErrorMessage(JSON.stringify(res.data));
                    }
                } catch (error) {
                    if (axios.isAxiosError(error)) {
                        // Now TypeScript knows error is of type AxiosError
                        const serverError = error as AxiosError;
                        if (serverError && serverError.response) {
                            setErrorMessage("Error: " + JSON.stringify(serverError.response.data));
                        } else {
                            setErrorMessage("An unexpected error occurred");
                        }
                    } else {
                        // Error is not from Axios
                        setErrorMessage("An unexpected error occurred");
                    }
                }
            }
        };

        return (
            <div className="flex min-h-screen flex-col">
                <Header/>
                <Container component="main">
                    <Paper elevation={3} sx={{mt: 4, p: 4}}>
                        <Grid container spacing={3} justifyContent="center">
                            <Grid item xs={12} md={12}>
                                <Typography variant="h5" gutterBottom sx={{mt: 2, mb: 2}}>
                                    Profile Information
                                </Typography>
                                <List sx={{width: '100%'}}>
                                    <ListItem>
                                        <ListItemAvatar>
                                            <Avatar>
                                                <EmailIcon/>
                                            </Avatar>
                                        </ListItemAvatar>
                                        <ListItemText primary="Username" secondary={username}/>
                                    </ListItem>
                                    <ListItem>
                                        <ListItemAvatar>
                                            <Avatar>
                                                <PersonIcon/>
                                            </Avatar>
                                        </ListItemAvatar>
                                        <ListItemText primary="First Name" secondary={firstName}/>
                                    </ListItem>
                                    <ListItem>
                                        <ListItemAvatar>
                                            <Avatar>
                                                <PersonIcon/>
                                            </Avatar>
                                        </ListItemAvatar>
                                        <ListItemText primary="Last Name" secondary={lastName}/>
                                    </ListItem>
                                    {/* Additional fields can be added in the same pattern */}
                                </List>
                            </Grid>
                            <Grid item xs={12} md={12}>
                                <Typography variant="h5" gutterBottom>Token Management</Typography>
                                {/* Token Generation and View */}
                                <Box sx={{mt: 2}}>
                                    {
                                        data && (
                                            <Button startIcon={<VpnKeyIcon/>} variant="outlined" color="primary"
                                                    onClick={handleGenerateToken} disabled={!userId}>
                                                {data?.authtoken_token.length > 0 ? 'Regenerate Token' : 'Generate Token'}
                                            </Button>)
                                    }
                                    {data && data?.authtoken_token.length > 0 && (
                                        <Alert severity="info" sx={{mt: 2}}>
                                            Your token is: {data?.authtoken_token[0]?.key}
                                        </Alert>
                                    )}
                                </Box>

                            </Grid>
                            <Divider/>
                            <Grid item xs={12} md={12}>

                                <Typography variant="h5" gutterBottom>Password Management</Typography>
                                {/* Password Reset Section */}
                                <Box sx={{mt: 4}}>
                                    <TextField
                                        label="Current Password"
                                        variant="outlined"
                                        type="password"
                                        fullWidth
                                        value={currentPassword}
                                        onChange={(e) => setCurrentPassword(e.target.value)}
                                        sx={{mb: 2}}
                                    />
                                    <TextField
                                        label="New Password"
                                        variant="outlined"
                                        type="password"
                                        fullWidth
                                        value={newPassword}
                                        onChange={(e) => setNewPassword(e.target.value)}
                                        sx={{mb: 2}}
                                    />
                                    <Button startIcon={<PasswordIcon/>} variant="contained" color="success"
                                            onClick={handleResetPassword} disabled={!(newPassword && currentPassword)}>
                                        Reset Password
                                    </Button>

                                    {/*    give a place for error hint*/}
                                    {errorMessage
                                        && (
                                            <Alert severity="error" sx={{mt: 2}}>
                                                {errorMessage}
                                            </Alert>
                                        )}
                                    {successMessage
                                        && (
                                            <Alert severity="success" sx={{mt: 2}}>
                                                {successMessage}
                                            </Alert>
                                        )}
                                </Box>

                            </Grid>
                        </Grid>
                    </Paper>
                </Container>
            </div>
        );
    }
;

export default isAuth(ProfilePage);