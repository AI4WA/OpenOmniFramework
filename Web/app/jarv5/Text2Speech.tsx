'use client'
import React, {useEffect} from "react";
import {useSubscription, gql} from "@apollo/client";
import {
    Typography,
    Grid,
    Paper,
    Box,
    List,
    ListItem,
    ListItemText,
    Divider
} from "@mui/material";

interface Text2SpeechProps {
    homeId: number | null;
}

const Text2Speech_SUBSCRIPTION = gql`
subscription Text2SpeechSubscription($homeId: bigint!) {
  hardware_text2speech(where: {home_id: {_eq: $homeId}}) {
    text
    created_at
  }
}
`

const Text2Speech: React.FC<Text2SpeechProps> = ({homeId}) => {

    const {data: speech2textData} = useSubscription(Text2Speech_SUBSCRIPTION, {
        variables: {homeId}
    })

    return (
        <Box sx={{padding: 0}}>
            <Typography variant="h6" gutterBottom>
                Jarv5 Response
            </Typography>
            <Paper elevation={1} sx={{padding: 1, border: 'none', boxShadow: 'none'}}>
                <List sx={{overflow: "auto", height: "32vh"}}>
                    {speech2textData?.hardware_text2speech.map((speech2text: any) => (
                        <div key={speech2text.created_at}>
                            <ListItem>
                                <ListItemText primary={speech2text.text} secondary={speech2text.created_at}/>
                            </ListItem>
                            <Divider/>
                        </div>
                    ))}
                </List>
            </Paper>
        </Box>
    );
}

export default Text2Speech;