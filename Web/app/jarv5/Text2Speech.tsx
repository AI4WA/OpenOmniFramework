'use client'
import React from "react";
import {useSubscription, gql} from "@apollo/client";
import {
    Typography,
    Paper,
    Box,
    List,
    ListItem,
    Divider,
} from "@mui/material";
import moment from "moment";
import Waveform from "@/app/jarv5/Waveform";


interface Text2SpeechProps {
    homeId: number | null;
}

interface Text2SpeechData {
    id: number;
    text: string;
    created_at: string;
    text2speech_file: string;
}

const Text2Speech_SUBSCRIPTION = gql`
subscription Text2SpeechSubscription($homeId: bigint!) {
  hardware_text2speech(where: {home_id: {_eq: $homeId}}, order_by: {created_at: desc}) {
      id
    text
    created_at
    text2speech_file
  }
}
`

const Text2Speech: React.FC<Text2SpeechProps> = ({homeId}) => {

    const {data: speech2textData} = useSubscription(Text2Speech_SUBSCRIPTION, {
        variables: {
            homeId: homeId
        }
    });

    return (
        <Box sx={{padding: 0}}>
            <Typography variant="h6" gutterBottom>
                Jarv5 Response
            </Typography>
            <Paper elevation={1} sx={{padding: 1, border: 'none', boxShadow: 'none', overflow: "auto", height: "32vh"}}>
                {speech2textData?.hardware_text2speech.map((speech: Text2SpeechData) => (
                    <div key={speech.id}>
                        <List>
                            <ListItem>
                                <Waveform speechId={speech?.id} modelName="text2speech"/>
                                <Box>
                                    <Typography variant="caption" display="block" gutterBottom>
                                        {moment(speech.created_at).format('MMMM Do hh:mm:ss a')} {/* Date formatting */}
                                    </Typography>
                                </Box>
                            </ListItem>
                            <Divider/>
                        </List>
                    </div>
                ))}
            </Paper>
        </Box>
    );
};


export default Text2Speech;