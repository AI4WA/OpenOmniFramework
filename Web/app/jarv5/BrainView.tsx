'use client'
import React from 'react'
import {Grid, List, Paper, Typography, ListItem, ListItemText} from "@mui/material";
import {useQuery, gql} from "@apollo/client";

interface BrainViewProps {
    selectedTextId: number | null
}

const DATA_TEXT_QUERY = gql`
query DataTextDetails($dataTextId: bigint!) {
  hardware_datatext(where: {id: {_eq: $dataTextId}}, order_by: {created_at: desc}) {
    text
    id
    hardware_emotiondetections(order_by: {created_at: desc})  {
      result
      id
    }
    hardware_llmresponses(order_by: {created_at: desc})  {
      result
      messages
    }
  }
}
`


const BrainView: React.FC<BrainViewProps> = (
    {selectedTextId}
) => {

    const {data} = useQuery(DATA_TEXT_QUERY, {
        variables: {dataTextId: selectedTextId}
    })

    const keyMapping: {
        [key: string]: string
    } = {
        M: 'MultiModality',
        T: 'Text',
        A: 'Audio',
        V: 'Video'
    };
    return (
        <>

            <Grid item xs={4}>
                <Paper sx={{
                    height: '100%', // Ensure it fills the parent's height
                    p: 1,
                    border: '1px solid black',
                }}>
                    <Typography variant="h6" component="h6" gutterBottom>
                        Emotion Detection
                    </Typography>
                    {/*    result will be in json {M: 0.2, V: 0.1 XXX}, SHOW THEN IN A LIST*/}
                    <List>
                        {['M', 'T', 'A', 'V'].map((key) => {
                            const readableName = keyMapping[key];  // Get readable name from keyMapping
                            const value = data?.hardware_datatext?.[0]?.hardware_emotiondetections?.[0]?.result?.[key] || "No Data"; // Providing a fallback value
                            return (
                                <ListItem key={key}>
                                    <ListItemText primary={`${readableName}: ${value}`}/>
                                </ListItem>
                            );
                        })}
                    </List>
                </Paper>
            </Grid>
            <Grid item xs={4}>
                <Paper sx={{
                    height: '100%', // Ensure it fills the parent's height
                    p: 1,
                    border: '1px solid black',
                }}>
                    <Typography variant="h6" component="h6" gutterBottom>
                        RAG
                    </Typography>
                    {/*    present the messages field here, will be quite long*/}
                    <Typography variant="body2" gutterBottom>
                        {data?.hardware_datatext?.[0]?.hardware_llmresponses?.[0]?.messages || "No Data"}
                    </Typography>
                </Paper>
            </Grid>
            <Grid item xs={4}>
                <Paper sx={{
                    height: '100%', // Ensure it fills the parent's height
                    p: 1,
                    border: '1px solid black',
                }}>
                    <Typography variant="h6" component="h6" gutterBottom>
                        LLM
                    </Typography>
                    <Typography variant="body2" gutterBottom>
                        {data?.hardware_datatext?.[0]?.hardware_llmresponses?.[0]?.result || "No Data"}
                    </Typography>
                </Paper>
            </Grid>

        </>
    )
}

export default BrainView