'use client'
import React from "react";
import {
    Typography,
    Card,
    CardContent,
    Box,
} from "@mui/material";
import Image from 'next/image';

interface HomeProps {
    homeId: number | null;
    homeData: {
        id: number;
        name: string;
        address: string;
    }[];
}

const Home: React.FC<HomeProps> = ({homeId, homeData}) => {
    const selectedHome = homeData?.find(home => home.id === homeId);

    return (
        <Card raised sx={{height: "100%", width: "100%"}}>
            <CardContent sx={{height: "100%"}}>
                <Box sx={{
                    height: "50%",
                    display: 'flex',
                    justifyContent: 'center',
                    flexDirection: 'column',
                    alignItems: 'center'
                }}>
                    {selectedHome ? (
                        <>
                            <Image src="/icons/blue-house.png" alt="Chat with Open Source LLM" width={64}
                                   height={64}/>
                            <Typography variant="h5" component="h2" gutterBottom>
                                {selectedHome.name}
                            </Typography>
                        </>
                    ) : (
                        <Typography color="text.secondary" align="center">
                            Home not found
                        </Typography>
                    )}
                </Box>
                <Box sx={{
                    height: "50%",
                    display: 'flex',
                    justifyContent: 'center',
                    flexDirection: 'column',
                    alignItems: 'center'
                }}>
                    <>
                        <Image src="/icons/JARV5.webp" alt="Chat with Open Source LLM" width={64}
                               height={64}/>
                        <Typography variant="h5" component="h2" gutterBottom>
                            Jarv5
                        </Typography>
                        <Typography color="text.secondary" align="center">
                            Aged Care AI Robot
                        </Typography>
                        <Typography color="text.secondary" align="center" variant="body2">
                            Health monitoring and Emotion support
                        </Typography>
                    </>

                </Box>
            </CardContent>
        </Card>
    );
};

export default Home;
