'use client'
import React, {useEffect, useState} from "react";
import Header from "@/components/Header";
import isAuth from "@/app/isAuth";
import {Grid, Paper, Typography} from '@mui/material';
import {useQuery, gql} from "@apollo/client";
import {useAppSelector} from "@/store";
import Home from "./Home"
import HardwareData from "@/app/jarv5/HardwareData";

const GET_HOME = gql`
query GetHome($userId: bigint!) {
    hardware_home(where: {user_id: {_eq: $userId}}) {
        id
        name
        address
    }
}`

const Jarv5 = () => {
    const userId = useAppSelector(state => state.auth.authState.userId)
    const [homeId, setHomeId] = useState<number | null>(null)
    const {data} = useQuery(GET_HOME, {
        variables: {userId}
    })

    useEffect(() => {
        if (data) {
            setHomeId(data.hardware_home[0].id)
        }
    }, [data])

    return (
        <div style={{display: 'flex', flexDirection: 'column', height: '100vh'}}> {/* Step 1 & 2 */}
            <Header/>
            <Grid container spacing={2}
                  sx={{flexGrow: 1, p: 1}}>
                {/* Vertical Navigation Bar */}
                <Grid item xs={2}>
                    <Paper sx={{height: '100%', p: 2, border: '1px solid black'}}>
                        <Home homeId={homeId} homeData={data?.hardware_home}/>
                    </Paper>
                </Grid>

                {/* Main Content Area */}
                <Grid item xs={10} container>
                    {/* Top Section - divided into two */}
                    <Grid item xs={12} container>
                        <Grid item xs={9}>
                            <Paper sx={{
                                height: '100%',
                                p: 2,
                                border: '1px solid black'
                            }}>

                                <HardwareData homeId={homeId}/>
                            </Paper>
                        </Grid>
                        <Grid item xs={3}>
                            <Paper sx={{
                                height: '100%',
                                p: 2,
                                border: '1px solid black'
                            }}>
                                <Typography variant="h5" component="h2" gutterBottom>
                                    Response Data
                                </Typography>
                            </Paper>
                        </Grid>
                    </Grid>

                    {/* Middle Thin Section */}
                    <Grid item xs={12} container>
                        <Grid item xs={12}>
                            <Paper sx={{
                                p: 2,

                                height: "100%",
                                border: '1px solid black'
                            }}>
                                <Typography variant="h5" component="h2" gutterBottom>
                                    Process
                                </Typography>
                            </Paper>
                        </Grid>
                    </Grid>

                    {/* Bottom Section - divided into three */}
                    <Grid item xs={12} container>
                        <Grid item xs={4}>
                            <Paper sx={{
                                height: '100%',
                                p: 2,
                                border: '1px solid black',

                            }}> <Typography variant="h5" component="h2" gutterBottom>
                                Emotion Detection
                            </Typography></Paper>
                        </Grid>
                        <Grid item xs={4}>
                            <Paper sx={{
                                height: '100%',
                                p: 2,
                                border: '1px solid black',

                            }}>
                                <Typography variant="h5" component="h2" gutterBottom>
                                    RAG
                                </Typography>
                            </Paper>
                        </Grid>
                        <Grid item xs={4}>
                            <Paper sx={{
                                height: '100%',
                                p: 2,
                                border: '1px solid black',
                            }}>
                                <Typography variant="h5" component="h2" gutterBottom>
                                    LLM
                                </Typography>
                            </Paper>
                        </Grid>
                    </Grid>
                </Grid>
            </Grid>

            <footer className="bg-gray-800 text-white text-center p-4">
                <p>Developed by
                    <a href="https://www.linkedin.com/in/pascalsun23/" target="_blank" rel="noopener noreferrer"
                       className="text-blue-400 hover:text-blue-300 mx-1">
                        Pascal Sun
                    </a>
                    supported by
                    <a href="https://nlp-tlp.org/" target="_blank" rel="noopener noreferrer"
                       className="text-blue-400 hover:text-blue-300 mx-1">
                        UWA NLP-TLP GROUP
                    </a>
                </p>
            </footer>
        </div>
    )
}

export default isAuth(Jarv5);
