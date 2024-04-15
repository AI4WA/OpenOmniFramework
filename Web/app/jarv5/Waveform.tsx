import React, {useEffect, useRef, useState} from "react";
import WaveSurfer from "wavesurfer.js";
import apiClient from "@/cloud/apiClient";
import {Box, IconButton} from "@mui/material";
import PauseCircleOutlineIcon from "@mui/icons-material/PauseCircleOutline";
import PlayCircleOutlineIcon from "@mui/icons-material/PlayCircleOutline";

interface WaveformProps {
    speechId: number;
    modelName: string
}

const Waveform: React.FC<WaveformProps> = ({speechId, modelName}) => {

    const waveformContainerRef = useRef<HTMLDivElement | null>(null);
    const waveSurferRef = useRef<WaveSurfer | null>(null);
    const [audioUrl, setAudioUrl] = useState<string | null>(null);
    const [isPlaying, setIsPlaying] = useState<boolean>(false);

    useEffect(() => {
        const fetchAudioUrl = async () => {
            try {
                if (modelName === 'text2speech') {
                    const res = await apiClient.post('/hardware/speech/',
                        {"text2speech_id": speechId});
                    if (res.status === 200) {
                        setAudioUrl(res.data?.tts_url);
                    } else {
                        console.error('Error fetching the audio URL:', res.statusText);
                    }
                } else if (modelName === 'data_audio') {
                    const res = await apiClient.post('/hardware/audio/get_audio_data/',
                        {
                            "audio_id": speechId,
                        });
                    if (res.status === 200) {
                        setAudioUrl(res.data?.audio_url);
                    } else {
                        console.error('Error fetching the audio URL:', res.statusText);
                    }
                }
            } catch (error) {
                console.error('Error fetching the audio URL:', error);
            }
        };

        fetchAudioUrl().then(() => {
        });

    }, [speechId, modelName]);

    useEffect(() => {
        if (audioUrl && waveformContainerRef.current && !waveSurferRef.current) {
            try {
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


                waveSurferRef.current.on('error', (error) => {
                    console.error('Error loading the audio:', error);
                    // Perform cleanup or state updates depending on the error
                    setAudioUrl(null)
                });
                // Event listeners
                waveSurferRef.current.on('play', () => setIsPlaying(true));
                waveSurferRef.current.on('pause', () => setIsPlaying(false));
                waveSurferRef.current.on('finish', () => setIsPlaying(false));
                waveSurferRef.current.load(audioUrl);
            } catch (error) {
                console.error('Error creating WaveSurfer:', error);
                setAudioUrl(null);
            }
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
            <IconButton onClick={togglePlayback} sx={{marginRight: 2}} disabled={!audioUrl}>
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

export default Waveform;