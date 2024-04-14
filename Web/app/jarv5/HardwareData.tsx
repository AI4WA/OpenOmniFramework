'use client'
import React, {useState} from "react";
import {
    Typography,
    Grid,
    Paper,
    Box,
    List,
    ListItem,
    ListItemText,
    Divider,
    IconButton,
    Dialog,
    DialogActions,
    DialogContent,
    Button
} from "@mui/material";
import {useSubscription, gql} from "@apollo/client";
import moment from "moment";
import Waveform from "@/app/jarv5/Waveform";
import PlayCircleOutlineIcon from '@mui/icons-material/PlayCircleOutline';  // Or PlayCircleFilledIcon
import apiClient from "@/cloud/apiClient";


interface HardwareDataProps {
    homeId: number | null;
}


interface AudioData {
    id: number,
    audio_file: string;
    created_at: string;
    start_time: string;
    hardware_device_mac_address: string;
    sequence_index: number;
    uid: string;
    end_time: string;
}

interface VideoData {
    id: number;
    video_file: string;
    created_at: string;
    uid: string;
    hardware_device_mac_address: string;
    video_record_minute: number;
}

interface TextData {
    id: number;
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
    id
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
    id
  }
}
`

const DATA_TEXT_SUBSCRIPTION = gql`
subscription DataTextSubscription($homeId: bigint!) {
  hardware_datatext(where: {home_id: {_eq: $homeId}}, order_by: {created_at: desc}) {
      id
    text
    created_at
  }
}
`

const HardwareData: React.FC<HardwareDataProps> = ({homeId}) => {
    const [open, setOpen] = useState(false);
    const [selectedVideo, setSelectedVideo] = useState(undefined);

    const handleClickOpen = async (videoId: number) => {
        const res = await apiClient.post('/hardware/video/get_video_data/',
            {
                "video_id": videoId,
            });
        if (res.status === 200) {
            const videoUrl = res.data?.video_url;
            console.log(videoUrl)
            setSelectedVideo(videoUrl);
            setOpen(true);
        } else {
            setOpen(false)
        }
    };

    const handleClose = () => {
        setOpen(false);
    };


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
                                                primary={<Waveform speechId={audio.id} modelName="data_audio"/>}
                                                secondary={`Created at: ${moment(audio.created_at).format('MMMM Do hh:mm:ss a')} | Audio: ${audio.audio_file}`}
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
                        <Paper elevation={1} sx={{padding: 1, overflow: "auto"}}>
                            <Typography variant="body2" gutterBottom>
                                Data Video
                            </Typography>
                            <List sx={{overflow: "auto", height: "13vh"}}>
                                {videoData?.hardware_datavideo.map((videoObj: VideoData, index: number) => (
                                    <React.Fragment key={index}>
                                        <ListItem>
                                            <ListItemText
                                                primary={`Video: ${videoObj.video_file}`}
                                                secondary={`Created at: ${moment(videoObj.created_at).format('MMMM Do hh:mm:ss a')}`}
                                            />
                                            <IconButton onClick={() => handleClickOpen(videoObj.id)} edge="end"
                                                        aria-label="play">
                                                <PlayCircleOutlineIcon/>
                                            </IconButton>
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
                    <Paper elevation={1} sx={{padding: 1}}>
                        <Typography variant="body2" gutterBottom>
                            Speech to Text
                        </Typography>
                        <List sx={{overflow: "auto", height: "13vh"}}>
                            {textData?.hardware_datatext.map((textObj: TextData, index: number) => (
                                <React.Fragment key={index}>
                                    <ListItem>
                                        <ListItemText
                                            primary={`${textObj.text}`}
                                            secondary={`Created at: ${moment(textObj.created_at).format('MMMM Do hh:mm:ss a')}`}
                                        />
                                    </ListItem>
                                    <Divider component="li"/>
                                </React.Fragment>
                            ))}
                        </List>
                    </Paper>
                </Grid>
            </Grid>
            <Dialog
                open={open}
                onClose={handleClose}
                aria-labelledby="video-playback-dialog"
                maxWidth="md"
                fullWidth
            >
                <DialogContent>
                    <video width="100%" controls>
                        <source src={selectedVideo}/>
                        Your browser does not support the video tag.
                    </video>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose} color="primary">
                        Close
                    </Button>
                </DialogActions>
            </Dialog>

        </Box>
    )
};

export default HardwareData;
