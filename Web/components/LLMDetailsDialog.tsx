'use client'

import React from 'react';
import moment from 'moment';

import {

    Dialog,
    DialogTitle,
    DialogContent,
    Grid,
    Typography,
    Accordion,
    AccordionSummary,
    ListItem,
    ListItemText,
    List,
    AccordionDetails
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';


interface Task {
    id: string;
    description: string;
    result_status: string;
    parameters: any; // Use the appropriate type based on your actual data structure
    created_at: string;
    name: string;
    user_id: string;
    updated_at: string;
    work_type: string;
    authenticate_user: {
        username: string;
    }
}

interface TaskDetailsDialogProps {
    task: Task;
    open: boolean;
    onClose: () => void;
}


const TaskDetailsDialog: React.FC<TaskDetailsDialogProps> = ({task, open, onClose}) => {
    return (
        <Dialog open={open} onClose={onClose} aria-labelledby="task-details-title" maxWidth="md" fullWidth>
            <DialogTitle id="task-details-title">Task Details</DialogTitle>
            <DialogContent dividers>
                <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                        <List dense>
                            <ListItem>
                                <ListItemText primary="Name" secondary={task.name}/>
                            </ListItem>
                            <ListItem>
                                <ListItemText primary="Status" secondary={task.result_status}/>
                            </ListItem>
                            <ListItem>
                                <ListItemText primary="Task Type" secondary={task.parameters?.llm_task_type}/>
                            </ListItem>
                            <ListItem>
                                <ListItemText primary="Prompt"
                                              secondary={task.parameters?.prompt || JSON.stringify(task.parameters?.messages)}/>
                            </ListItem>
                        </List>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <List dense>
                            <ListItem>
                                <ListItemText primary="Work Type" secondary={task.work_type}/>
                            </ListItem>
                            <ListItem>
                                <ListItemText primary="Updated At"
                                              secondary={moment(task.updated_at).format('YYYY-MM-DD HH:mm:ss')}/>
                            </ListItem>
                            <ListItem>
                                <ListItemText primary="Created At"
                                              secondary={moment(task.created_at).format('YYYY-MM-DD HH:mm:ss')}/>
                            </ListItem>
                        </List>
                    </Grid>
                </Grid>

                {/* Parameters as expandable content */}
                <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon/>}>
                        <Typography>Parameters</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                        <Typography>
                            {JSON.stringify(task.parameters, null, 2)}
                        </Typography>
                    </AccordionDetails>
                </Accordion>

                {/* Descriptions as expandable content */}
                <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon/>}>
                        <Typography>Descriptions</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                        <Typography>
                            {task.description}
                        </Typography>
                    </AccordionDetails>
                </Accordion>
                {/* Include other task details as needed */}
            </DialogContent>
        </Dialog>
    )
}

export default TaskDetailsDialog;

export type {Task, TaskDetailsDialogProps};