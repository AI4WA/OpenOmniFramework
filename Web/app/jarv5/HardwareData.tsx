'use client'
import React from "react";
import {
    Typography, Grid, Paper, Box,
    List, ListItem, ListItemText, Divider
} from "@mui/material";
import {useSubscription, gql} from "@apollo/client";

interface HardwareDataProps {
    homeId: number | null;
}


const DATA_AUDIO_SUBSCRIPTION = gql`
subscription DataAudioSubscription($homeId: bigint!) {
  hardware_dataaudio(where: {home_id: {_eq: $homeId}}) {
    audio_file
    created_at
    start_time
    hardware_device_mac_address
    sequence_index
    uid
    end_time
  }
}
`

const DATA_VIDEO_SUBSCRIPTION = gql`
subscription DataVideoSubscription($homeId: bigint!) {
  hardware_datavideo(where: {home_id: {_eq: $homeId}}) {
    video_file
    created_at
    uid
    hardware_device_mac_address
    video_record_minute
  }
}
`

const DATA_TEXT_SUBSCRIPTION = gql`
subscription DataTextSubscription($homeId: bigint!) {
  hardware_datatext(where: {home_id: {_eq: $homeId}}) {
    text
    created_at
  }
}
`

const HardwareData: React.FC<HardwareDataProps> = ({homeId}) => {

    const {data: audioData} = useSubscription(DATA_AUDIO_SUBSCRIPTION, {
        variables: {homeId}
    })

    const {data: videoData} = useSubscription(DATA_VIDEO_SUBSCRIPTION, {
        variables: {homeId}
    })

    const {data: textData} = useSubscription(DATA_TEXT_SUBSCRIPTION, {
        variables: {homeId}
    })


    return (
        <Box sx={{padding: 2}}>
            <Typography variant="h5" gutterBottom>
                Hardware Data
            </Typography>
            <Grid container spacing={2}>
                {/* Upper section */}
                <Grid item xs={12} container spacing={2}>
                    {/* Audio Data */}
                    <Grid item xs={12} md={6}>
                        <Paper elevation={2} sx={{height: '100%', padding: 2, overflow: "auto"}}>
                            <Typography variant="h6" gutterBottom>
                                Data Audio
                            </Typography>
                            {/* Insert audio data content here */}
                            <List>
                                {audioData?.hardware_dataaudio.map((audio, index) => (
                                    <React.Fragment key={index}>
                                        <ListItem>
                                            <ListItemText
                                                primary={`Audio File: ${audio.audio_file}/${audio.uid}`}
                                                secondary={`Created at: ${audio.created_at}`}
                                            />
                                        </ListItem>
                                        <Divider component="li"/>
                                    </React.Fragment>
                                ))}
                            </List>
                        </Paper>
                    </Grid>
                    {/* Speech to Text Results */}
                    <Grid item xs={12} md={6}>
                        <Paper elevation={2} sx={{height: '100%', padding: 2, overflow: "auto"}}>
                            <Typography variant="h6" gutterBottom>
                                Speech to Text
                            </Typography>
                            <List>
                                {textData?.hardware_datatext.map((textObj, index) => (
                                    <React.Fragment key={index}>
                                        <ListItem>
                                            <ListItemText
                                                primary={`STT: ${textObj.text}`}
                                                secondary={`Created at: ${textObj.created_at}`}
                                            />
                                        </ListItem>
                                        <Divider component="li"/>
                                    </React.Fragment>
                                ))}
                            </List>
                        </Paper>
                    </Grid>
                </Grid>
                {/* Lower section */}
                <Grid item xs={12}>
                    <Paper elevation={2} sx={{padding: 2, height: '100%', overflow: "auto"}}>
                        <Typography variant="h6" gutterBottom>
                            Data Video
                        </Typography>
                        <List>
                            {videoData?.hardware_datavideo.map((videoObj, index) => (
                                <React.Fragment key={index}>
                                    <ListItem>
                                        <ListItemText
                                            primary={`STT: ${videoObj.video_file}/${videoObj.video_record_minute}`}
                                            secondary={`Created at: ${videoObj.created_at}`}
                                        />
                                    </ListItem>
                                    <Divider component="li"/>
                                </React.Fragment>
                            ))}
                        </List>
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
};

export default HardwareData;
