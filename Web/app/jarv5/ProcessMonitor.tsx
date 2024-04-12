'use client'
import React from "react";
import {Typography, Card, CardContent, Box, Grid} from "@mui/material";
import {useSubscription, gql} from "@apollo/client";


interface ProcessMonitorProps {
    homeId: number | null;
}

const ProcessMonitor_SUBSCRIPTION = gql`
subscription ProcessMonitor($homeId: bigint!) {
  hardware_dataaudio(where: {home_id: {_eq: $homeId}}) {
    id
    audio_file
    sequence_index
    start_time
    end_time
    uid
    hardware_datatexts {
      created_at
      text
      pipeline_triggered
      translation_in_seconds
      hardware_emotiondetections {
        created_at
        result
      }
      hardware_llmresponses {
        messages
        result
        created_at
      }
      hardware_text2speeches {
        text
        played
        created_at
      }
    }
  }
}
`

const ProcessMonitor: React.FC<ProcessMonitorProps> = ({homeId}) => {

    const {data: processMonitorData} = useSubscription(ProcessMonitor_SUBSCRIPTION, {
        variables: {homeId}
    })
    return (
        <div>
            <h1>ProcessMonitor</h1>
        </div>
    );
}

export default ProcessMonitor;