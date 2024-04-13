'use client'
import React, {useEffect, useState, useRef} from "react";
import {useSubscription, gql} from "@apollo/client";
import {
    Typography,
    Paper,
    Box,
    List,
    ListItem,
    Divider,
    IconButton
} from "@mui/material";
import PlayCircleOutlineIcon from '@mui/icons-material/PlayCircleOutline';
import PauseCircleOutlineIcon from '@mui/icons-material/PauseCircleOutline';
import apiClient from "@/cloud/apiClient";
import WaveSurfer from 'wavesurfer.js';
import moment from "moment";


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
            <Paper elevation={1} sx={{padding: 1, border: 'none', boxShadow: 'none'}}>
                {speech2textData?.hardware_text2speech.map((speech: Text2SpeechData) => (
                    <div key={speech.id}>
                        <List>
                            <ListItem>
                                <Waveform speechId={speech?.id}/>
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


interface WaveformProps {
    speechId: number;
}

const Waveform: React.FC<WaveformProps> = ({speechId}) => {

    const waveformContainerRef = useRef<HTMLDivElement | null>(null);
    const waveSurferRef = useRef<WaveSurfer | null>(null);
    const [audioUrl, setAudioUrl] = useState<string | null>(null);
    const [isPlaying, setIsPlaying] = useState<boolean>(false);

    useEffect(() => {
        const fetchAudioUrl = async () => {
            try {
                const res = await apiClient.post('/hardware/speech/',
                    {"text2speech_id": speechId});
                if (res.status === 200) {
                    setAudioUrl(res.data?.tts_url);
                } else {
                    console.error('Error fetching the audio URL:', res.statusText);
                }
            } catch (error) {
                console.error('Error fetching the audio URL:', error);
            }
        };

        fetchAudioUrl().then(r => console.log(r));

    }, [speechId]);

    useEffect(() => {
        if (audioUrl && waveformContainerRef.current && !waveSurferRef.current) {
            waveSurferRef.current = WaveSurfer.create({
                container: waveformContainerRef.current,
                waveColor: 'blue',
                progressColor: 'blue',
                cursorColor: 'navy',
                barWidth: 2,
                barRadius: 1,
                height: 50,
                normalize: true,
                hideScrollbar: true,
            });

            waveSurferRef.current.load(audioUrl);

            // Event listeners
            waveSurferRef.current.on('play', () => setIsPlaying(true));
            waveSurferRef.current.on('pause', () => setIsPlaying(false));
            waveSurferRef.current.on('finish', () => setIsPlaying(false));
        }

        return () => {
            if (waveSurferRef.current) {
                waveSurferRef.current.destroy();
                waveSurferRef.current = null;
            }
        };
    }, [audioUrl]);

    const togglePlayback = () => {
        if (waveSurferRef.current) {
            if (waveSurferRef.current.isPlaying()) {
                waveSurferRef.current.pause();
            } else {
                waveSurferRef.current.play();
            }
        }
    };

    return (
        <Box display="flex" alignItems="center" sx={{width: "100%"}}>
            <IconButton onClick={togglePlayback} sx={{marginRight: 2}}>
                {isPlaying ? <PauseCircleOutlineIcon/> : <PlayCircleOutlineIcon/>}
            </IconButton>
            <div ref={waveformContainerRef} style={{
                flexGrow: 1, // Make it take the remaining space
                height: '50px',
                borderRadius: '5px',
                overflow: 'hidden',
                backgroundColor: '#f5f5f5',
            }}/>
        </Box>
    );
};


export default Text2Speech;