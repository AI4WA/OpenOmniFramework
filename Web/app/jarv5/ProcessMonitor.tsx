'use client'
import React, {useEffect} from "react";
import {useSubscription, gql} from "@apollo/client";
import {
    Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Card, CardContent, Box, Grid
} from "@mui/material";

const ProcessMonitor_SUBSCRIPTION = gql`
subscription ProcessMonitor($homeId: bigint!) {
  hardware_dataaudio(where: {home_id: {_eq: $homeId}}, order_by: {start_time: desc}) {
    id
    audio_file
    sequence_index
    start_time
    end_time
    uid
    hardware_datatexts(order_by: {created_at: desc}) {
        id
      created_at
      text
      pipeline_triggered
      translation_in_seconds
      hardware_emotiondetections(order_by: {created_at: desc}) {
        created_at
        result
      }
      hardware_llmresponses(order_by: {created_at: desc})  {
        messages
        result
        created_at
      }
      hardware_text2speeches(order_by: {created_at: desc})  {
        text
        played
        created_at
        text2speech_file
      }
    }
  }
}
`;

interface ProcessMonitorProps {
    homeId: number | null;
    selectedTextId: number | null;
    setSelectedTextId: (textId: number | null) => void;
}

interface AudioData {
    audio_file: string;
    created_at: string;
    start_time: string;
    hardware_device_mac_address: string;
    sequence_index: number;
    uid: string;
    end_time: string;
    hardware_datatexts: TextData[];

}

interface TextData {
    id: number,
    text: string;
    created_at: string;
    pipeline_triggered: boolean;
    translation_in_seconds: number;
    hardware_emotiondetections: {
        created_at: string;
        result: {
            M: number;
        };
    }[];
    hardware_llmresponses: {
        messages: string;
        result: string;
        created_at: string;
    }[];
    hardware_text2speeches: {
        text: string;
        played: boolean;
        created_at: string;
        text2speech_file: string;
    }[];
}

const ProcessMonitor: React.FC<ProcessMonitorProps> = ({
                                                           homeId,
                                                           setSelectedTextId,
                                                           selectedTextId
                                                       }) => {
    const {data: processMonitorData} = useSubscription(ProcessMonitor_SUBSCRIPTION, {
        variables: {homeId}
    });

    // if the processMonitorData is updated, then update the selectedTextId to the latest one
    useEffect(() => {
        if (processMonitorData) {
            setSelectedTextId(processMonitorData.hardware_dataaudio[0].hardware_datatexts[0].id);
        }
    }, [processMonitorData, setSelectedTextId]);

    return (
        <Box>
            <Typography variant="h4" gutterBottom>
                Process Monitor
            </Typography>
            <TableContainer component={Paper} sx={{overflow: "auto"}}>
                <Table aria-label="process monitor table">
                    <TableHead>
                        <TableRow>
                            <TableCell>Audio</TableCell>
                            <TableCell>Text</TableCell>
                            <TableCell>Responding</TableCell>
                            <TableCell>Emotion</TableCell>
                            <TableCell>RAG</TableCell>
                            <TableCell>LLM</TableCell>
                            <TableCell>TTS</TableCell>
                            <TableCell>Played</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {processMonitorData?.hardware_dataaudio.map((audioData: AudioData) => (
                            audioData.hardware_datatexts.map((textData: TextData) => (
                                <TableRow key={textData.created_at}
                                          selected={selectedTextId === textData.id}
                                          onClick={() => setSelectedTextId(textData.id)}
                                >
                                    <TableCell>{audioData.audio_file}</TableCell>
                                    <TableCell>{textData.text}</TableCell>
                                    <TableCell>{textData.pipeline_triggered ? "Yes" : "No"}</TableCell>
                                    <TableCell>
                                        {textData.hardware_emotiondetections && textData.hardware_emotiondetections.length > 0 && textData.hardware_emotiondetections[0].result
                                            ? textData.hardware_emotiondetections[0].result?.M > 0
                                                ? "Positive"
                                                : textData.hardware_emotiondetections[0].result?.M === 0
                                                    ? "Neutral"
                                                    : "Negative"
                                            : "No detection"}
                                    </TableCell>
                                    <TableCell>
                                        {textData.hardware_llmresponses.length > 0 ? "Processed" : "Waiting"}
                                    </TableCell>
                                    <TableCell>{textData.hardware_llmresponses.length > 0 ? "Processed" : "Waiting"}</TableCell>
                                    <TableCell>
                                        {textData.hardware_text2speeches?.[0]?.text2speech_file ? "Generated" : "Waiting"}
                                    </TableCell>
                                    <TableCell>{textData.hardware_text2speeches.map(tts => tts.played ? "Yes" : "No").join(", ")}</TableCell>
                                </TableRow>
                            ))
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </Box>
    );
};

export default ProcessMonitor;

