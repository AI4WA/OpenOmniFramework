'use client'
import React from "react";
import { Typography, Card, CardContent, Box, Grid } from "@mui/material";

interface HomeProps {
    homeId: number | null;
    homeData: {
        id: number;
        name: string;
        address: string;
    }[];
}

const Home: React.FC<HomeProps> = ({ homeId, homeData }) => {
    const selectedHome = homeData?.find(home => home.id === homeId);

    return (
        <Card raised>
            <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'center', flexDirection: 'column', alignItems: 'center' }}>
                    {selectedHome ? (
                        <>
                            <Typography variant="h5" component="h2" gutterBottom>
                                {selectedHome.name}
                            </Typography>
                            <Grid container spacing={1} justifyContent="center">
                                <Grid item xs={12}>
                                    <Typography variant="body2" color="text.secondary" align="left">
                                        {selectedHome.address}
                                    </Typography>
                                </Grid>
                            </Grid>
                        </>
                    ) : (
                        <Typography color="text.secondary" align="center">
                            Home not found
                        </Typography>
                    )}
                </Box>
            </CardContent>
        </Card>
    );
};

export default Home;
