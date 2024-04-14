'use client'
import React, {useEffect, useState} from "react";
import Header from "@/components/Header";
import isAuth from "@/app/isAuth";
import {Grid, Paper} from '@mui/material';
import {useQuery, gql} from "@apollo/client";
import {useAppSelector} from "@/store";
import Home from "./Home"
import HardwareData from "@/app/jarv5/HardwareData";
import Text2Speech from "@/app/jarv5/Text2Speech";
import ProcessMonitor from "@/app/jarv5/ProcessMonitor";
import BrainView from "@/app/jarv5/BrainView";

const GET_HOME = gql`
query GetHome {
    hardware_home{
        id
        name
        address
    }
}`

const Jarv5 = () => {
    const userId = useAppSelector(state => state.auth.authState.userId)
    const [homeId, setHomeId] = useState<number | null>(null)
    const [selectedTextId, setSelectedTextId] = useState<number | null>(null)
    const {data} = useQuery(GET_HOME, {
        variables: {userId}
    })

    useEffect(() => {
        if (data) {
            setHomeId(data.hardware_home[0]?.id)
        }
    }, [data])

    return (
        <div style={{display: 'flex', flexDirection: 'column', height: '100vh'}}> {/* Step 1 & 2 */}
            <Header/>

            <Grid container spacing={2} sx={{flexGrow: 1, overflow: 'hidden'}}>
                {/* Vertical Navigation Bar */}
                <Grid item xs={2} sx={{
                    height: "calc(100vh - 124px)",
                }}>
                    <Paper sx={{
                        height: '100%',
                        width: '100%',
                        p: 1, border: '1px solid black',
                        display: 'flex', justifyContent: 'center', flexDirection: 'column', alignItems: 'center'
                    }}>
                        <Home homeId={homeId} homeData={data?.hardware_home}/>
                    </Paper>
                </Grid>
                <Grid item xs={12} container
                      style={{display: 'flex', flexDirection: 'column', flex: 1, height: "calc(100vh - 124px)"}}>
                    {/* Top Section - divided into two */}
                    <Grid item xs={12} container style={{flex: 1}}>
                        <Grid item xs={8}>
                            <Paper sx={{
                                p: 1,
                                border: '1px solid black',
                                height: '100%', // Ensure it fills the parent's height
                            }}>
                                <HardwareData homeId={homeId}/>
                            </Paper>
                        </Grid>
                        <Grid item xs={4}>
                            <Paper sx={{
                                height: '100%',
                                p: 1,
                                border: '1px solid black',
                                overflow: "auto"
                            }}>
                                <Text2Speech homeId={homeId}/>
                            </Paper>
                        </Grid>
                    </Grid>

                    {/* Middle Thin Section */}
                    <Grid item xs={12} container style={{flex: 1}}>
                        <Grid item xs={12}>
                            <Paper sx={{
                                p: 1,
                                height: "100%", // Ensure it fills the parent's height
                                border: '1px solid black',
                                overflow: "auto"
                            }}>
                                <ProcessMonitor homeId={homeId}
                                                selectedTextId={selectedTextId}
                                                setSelectedTextId={setSelectedTextId}
                                />
                            </Paper>
                        </Grid>
                    </Grid>

                    <Grid item xs={12} container style={{flex: 1, overflow: "auto"}}>
                        <BrainView
                            selectedTextId={selectedTextId}
                        />
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
