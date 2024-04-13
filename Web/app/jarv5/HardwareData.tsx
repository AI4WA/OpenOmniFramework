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


interface AudioData {
    audio_file: string;
    created_at: string;
    start_time: string;
    hardware_device_mac_address: string;
    sequence_index: number;
    uid: string;
    end_time: string;
}

interface VideoData {
    video_file: string;
    created_at: string;
    uid: string;
    hardware_device_mac_address: string;
    video_record_minute: number;
}

interface TextData {
    text: string;
    created_at: string;
}


const DATA_AUDIO_SUBSCRIPTION = gql`
subscription DataAudioSubscription($homeId: bigint!) {
  hardware_dataaudio(where: {home_id: {_eq: $homeId}}, order_by: {created_at: desc}) {
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
  hardware_datavideo(where: {home_id: {_eq: $homeId}}, order_by: {created_at: desc}) {
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
  hardware_datatext(where: {home_id: {_eq: $homeId}}, order_by: {created_at: desc}) {
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
        <Box sx={{padding: 0, height: '100%'}}>
            <Typography variant="h6" gutterBottom>
                Hardware Data
            </Typography>
            <Grid container spacing={1}>
                {/* Upper section for audio data and speech to text results */}
                <Grid item xs={12} container spacing={1}>
                    {/* Audio Data */}
                    <Grid item xs={12} md={6}>
                        <Paper elevation={1} sx={{padding: 1}}>
                            <Typography variant="body2" gutterBottom>
                                Data Audio
                            </Typography>
                            <List sx={{overflow: "auto", height: "13vh"}}>
                                {audioData?.hardware_dataaudio.map((audio: AudioData, index: number) => (
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
                        <Paper elevation={1} sx={{padding: 1}}>
                            <Typography variant="body2" gutterBottom>
                                Speech to Text
                            </Typography>
                            <List sx={{overflow: "auto", height: "13vh"}}>
                                {textData?.hardware_datatext.map((textObj: TextData, index: number) => (
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
                {/* Lower section for video data */}
                <Grid item xs={12}>
                    <Paper elevation={1} sx={{padding: 1, overflow: "auto"}}>
                        <Typography variant="body2" gutterBottom>
                            Data Video
                        </Typography>
                        <List sx={{overflow: "auto", height: "13vh"}}>
                            {videoData?.hardware_datavideo.map((videoObj: VideoData, index: number) => (
                                <React.Fragment key={index}>
                                    <ListItem>
                                        <ListItemText
                                            primary={`Video: ${videoObj.video_file}/${videoObj.video_record_minute} min`}
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
    )
};

export default HardwareData;
