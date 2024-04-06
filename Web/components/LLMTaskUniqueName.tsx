'use client'
import React from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    Table,
    TableBody,
    TableCell,
    Button,
    CircularProgress,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
} from '@mui/material';
import {llmDownloadTaskName, llmDownloadOutputCSV} from '@/cloud/utils/llm_create_task';

interface DownloadLink {
    progress: string;
    download_link: string;
    id: number;
}

interface LLMTaskUniqueNameProps {
    open: boolean;
    onClose: () => void;
    tasks: {
        name: string;
        count: number
        downloadlink: DownloadLink[]
    }[];
}

const LLMTaskUniqueName: React.FC<LLMTaskUniqueNameProps> = ({open, onClose, tasks}) => {


    const downloadFileClick = (taskId: number) => async () => {
        console.log('Downloading file with taskId:', taskId);
        const res = await llmDownloadOutputCSV(taskId);
        console.log('Download response:', res);
        window.open(res.download_link, '_blank');
    }

    const requestDownload = (name: string) => async () => {
        console.log('Requesting download for:', name);
        const response = await llmDownloadTaskName(name);
        console.log('Response:', response);
    }

    return (
        <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
            <DialogTitle>Unique Names for Results</DialogTitle>
            <DialogContent>
                <TableContainer component={Paper}>
                    <Table aria-label="simple table">
                        <TableHead>
                            <TableRow>
                                <TableCell>Name</TableCell>
                                <TableCell align="center">Count</TableCell>
                                <TableCell align="center">Download</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {tasks.map((task) => (
                                <TableRow
                                    key={task.name}
                                    sx={{'&:last-child td, &:last-child th': {border: 0}}}
                                >
                                    <TableCell component="th" scope="row">
                                        {task.name}
                                    </TableCell>
                                    <TableCell align="center">{task.count}</TableCell>
                                    <TableCell align="center">
                                        {(task.downloadlink.length === 0
                                            || task.downloadlink[0].progress === 'failed'
                                            || task.downloadlink[0].progress === 'cancelled'
                                        ) ? (
                                            <Button variant="contained"
                                                    onClick={requestDownload(task.name)}
                                            >Request</Button>
                                        ) : task.downloadlink?.[0].progress !== 'completed' ? (
                                            // show a loading button if the download is in progress
                                            <Button variant="contained" disabled>
                                                <CircularProgress size={24}/>
                                            </Button>
                                        ) : (
                                            <Button variant="contained" component="a" download
                                                    onClick={downloadFileClick(task.downloadlink?.[0].id)}>
                                                Download
                                            </Button>
                                        )}
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </DialogContent>
        </Dialog>
    );
};

export default LLMTaskUniqueName;
