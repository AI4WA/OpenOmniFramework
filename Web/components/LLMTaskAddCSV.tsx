'use client'
// pages/create-tasks.js
import React, {useState, useRef} from 'react';
import Papa from 'papaparse';
import {
    Button,
    Container,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Box,
    AlertColor,
} from '@mui/material';
import {llmCreateTask} from '@/cloud/utils/llm_create_task';

interface SnackbarState {
    message: string;
    open: boolean;
    severity:  AlertColor
}

interface CreateTasksCSVProps {
    setSnackbar: (state: SnackbarState) => void;
}

interface TaskData {
    name: string;
    task_type: string;
    prompt: string;
    model_name: string;
    llm_task_type: string;

    [key: string]: any; // Allow other fields dynamically
}

const CreateTasks: React.FC<CreateTasksCSVProps> = ({setSnackbar}) => {
    const [tasks, setTasks] = useState<TaskData[]>([]);
    const fileInputRef = useRef<HTMLInputElement>(null); // Step 1: useRef to reference the file input

    // Function to handle file input change and parse the CSV file
    const handleFileSelect = (file: File) => {
        Papa.parse(file, {
            complete: (result) => {
                validateAndCreateTasks(result.data as TaskData[]);
            },
            header: true,
            skipEmptyLines: true,
        });
    };

    // Function to validate data and create tasks
    const validateAndCreateTasks = (data: TaskData[]) => {
        const isValid = data.every(entry => {
            // Assuming 'name' and 'prompt' are required fields
            return entry.name && entry.prompt && entry.model_name && entry.llm_task_type;
        });

        if (!isValid) {
            console.error('Some entries are missing required fields.');
            return;
        }
        setTasks([...tasks, ...data])
    };

    const createLLMTaskEach = async (taskData: TaskData) => {
        try {
            const result = await llmCreateTask({
                name: taskData.name,
                task_type: taskData.task_type,
                prompt: taskData.prompt,
                model_name: taskData.model_name,
                llm_task_type: taskData.llm_task_type,
            })
            console.log('LLM task created:', result);
            setSnackbar({
                message: `LLM task created: ${taskData.prompt}`,
                open: true,
                severity: 'success',
            });
        } catch (error) {
            console.error('Error creating LLM task:', error);
            setSnackbar({
                message: `Error creating LLM task: ${taskData.prompt}`,
                open: true,
                severity: 'error',
            });
        }
    };


    const handleConfirmTasks = async () => {
        for (const task of tasks) {
            await createLLMTaskEach(task);
        }
        // Clear tasks after creation
        setTasks([]);
    };
    const handleCancelTasks = () => {
        setTasks([]); // Clear the tasks array, effectively "canceling" the operation
        if (fileInputRef.current) {
            fileInputRef.current.value = ''; // This clears the file input
        }
    };
    return (
        <Container maxWidth="md">
            <Box sx={{marginTop: 2, display: 'flex', alignItems: 'center', gap: 1}}>
                <Button variant="contained" component="label">
                    Upload CSV
                    <input
                        type="file"
                        hidden
                        accept=".csv"
                        ref={fileInputRef}
                        onChange={(e) => {
                            if (e.target.files && e.target.files[0]) handleFileSelect(e.target.files[0]);
                        }}
                    />
                </Button>

                {tasks.length > 0 && (
                    <>
                        <Button variant="outlined" color="secondary" onClick={handleCancelTasks}>
                            Clear
                        </Button>
                        <Button variant="contained" color="primary" onClick={handleConfirmTasks}>
                            Create
                        </Button>
                    </>
                )}
            </Box>

            <TableContainer component={Paper} sx={{mt: 2}}>
                <Table aria-label="tasks table">
                    <TableHead>
                        <TableRow>
                            <TableCell>name</TableCell>
                            <TableCell>task_type</TableCell>
                            <TableCell>prompt</TableCell>
                            <TableCell>model_name</TableCell>
                            <TableCell>llm_task_type</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {tasks.map((task, index) => (
                            <TableRow key={index}>
                                <TableCell>{task.name}</TableCell>
                                <TableCell>{task.task_type}</TableCell>
                                <TableCell>{task.prompt}</TableCell>
                                <TableCell>{task.model_name}</TableCell>
                                <TableCell>{task.llm_task_type}</TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </Container>
    );
};

export default CreateTasks;
