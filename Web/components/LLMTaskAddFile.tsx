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
import {llmCreateTask, llmCustomCreateTask} from '@/cloud/utils/llm_create_task';

interface SnackbarState {
    message: string;
    open: boolean;
    severity: AlertColor
}

interface CreateTasksCSVProps {
    setSnackbar: (state: SnackbarState) => void;
}

interface Message {
    role: "system" | "user" | "assistant" | "function";
    content: string;
}

interface TaskData {
    name: string;
    task_type: string;
    prompt: string;
    model_name: string;
    llm_task_type: string;
    messages: Message[];

    [key: string]: any; // Allow other fields dynamically
}


const CreateTasks: React.FC<CreateTasksCSVProps> = ({setSnackbar}) => {
    const [tasks, setTasks] = useState<TaskData[]>([]);
    const fileInputRef = useRef<HTMLInputElement>(null); // Step 1: useRef to reference the file input
    const jsonInputRef = useRef<HTMLInputElement>(null); // Step 1: useRef to reference the file input
    const [customTask, setCustomTask] = useState<boolean>(false)

    // Function to handle file input change and parse the CSV file
    const handleFileSelect = (file: File) => {
        setCustomTask(false)
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
            if (customTask) {
                const result = await llmCustomCreateTask({
                    name: taskData.name,
                    task_type: taskData.task_type,
                    messages: taskData.messages,
                    model_name: taskData.model_name,
                    llm_task_type: taskData.llm_task_type,
                })
                console.log('LLM task created:', result);
                setSnackbar({
                    message: `LLM task created: ${JSON.stringify(taskData.messages)}`,
                    open: true,
                    severity: 'success',
                });
            } else {
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
            }

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
        if (jsonInputRef.current) {
            jsonInputRef.current.value = ''; // This clears the file input
        }
        if (fileInputRef.current) {
            fileInputRef.current.value = ''; // This clears the file input
        }
        setCustomTask(false)
    };

    const handleCancelTasks = () => {
        setTasks([]); // Clear the tasks array, effectively "canceling" the operation
        if (fileInputRef.current) {
            fileInputRef.current.value = ''; // This clears the file input
        }
        if (jsonInputRef.current) {
            jsonInputRef.current.value = ''; // This clears the file input
        }
        setCustomTask(false)
    };

    const handleJsonFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files.length > 0) {
            setCustomTask(true)

            const file = event.target.files[0];
            if (!file) {
                return;
            }

            const reader = new FileReader();
            reader.onload = (e: ProgressEvent<FileReader>) => {
                try {
                    const result = (e.target as FileReader).result;
                    if (typeof result !== 'string') {
                        throw new Error('Invalid file content');
                    }
                    const data = JSON.parse(result) as TaskData[];
                    console.log("JSON data:", data);
                    // loop and validate data
                    const isValid = data.every(entry => {
                        // Assuming 'name' and 'messages' are required fields
                        // also we need to check the messages array item are Message type
                        const hasRequiredFields = entry.name && Array.isArray(entry.messages) && entry.model_name && entry.llm_task_type;

                        // Validate each message in the 'messages' array, if it exists
                        const messagesValid = entry.messages ? entry.messages.every((message: Message) => message.role && message.content) : false;
                        // also need to check the role is one of the valid roles
                        const validRoles = ["system", "user", "assistant", "function"];
                        const messagesRolesValid = entry.messages ? entry.messages.every((message: Message) => validRoles.includes(message.role)) : false;
                        console.log("messagesRolesValid", messagesRolesValid)
                        console.log("messagesValid", messagesValid)
                        console.log("hasRequiredFields", hasRequiredFields)
                        return hasRequiredFields && messagesValid && messagesRolesValid;
                    });
                    if (!isValid) {
                        setSnackbar({
                            message: `Some entries are missing required fields.`,
                            open: true,
                            severity: 'error',
                        });
                        if (jsonInputRef.current) jsonInputRef.current.value = ''; // This clears the file input
                        return;
                    }
                    setTasks([...tasks, ...data])
                } catch (error) {
                    console.error("Error parsing JSON:", error);
                    // Update the state to indicate an error, or handle it otherwise
                }
            };
            reader.onerror = (error) => console.error("File reading error:", error);
            reader.readAsText(file);
        } else {
            setSnackbar({
                message: `No file selected.`,
                open: true,
                severity: 'error',
            });
        }
    };

    return (
        <Container maxWidth="md">
            <Box sx={{marginTop: 2, display: 'flex', alignItems: 'center', gap: 1}}>
                <Button variant="contained" component="label" disabled={customTask}>
                    Upload CSV
                    <input
                        type="file"
                        hidden
                        accept=".csv"
                        disabled={customTask}
                        ref={fileInputRef}
                        onChange={(e) => {
                            if (e.target.files && e.target.files[0]) handleFileSelect(e.target.files[0]);
                        }}
                    />
                </Button>
                <Button variant="contained" component="label" disabled={!customTask && (tasks.length !== 0)}>
                    Upload JSON
                    <input
                        type="file"
                        hidden
                        accept=".json"
                        onChange={handleJsonFileChange} // New JSON file handling
                        ref={jsonInputRef}
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
                            <TableCell>{customTask ? "messages" : "prompt"}</TableCell>
                            <TableCell>model_name</TableCell>
                            <TableCell>llm_task_type</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {tasks.map((task, index) => (
                            <TableRow key={index}>
                                <TableCell>{task.name}</TableCell>
                                <TableCell>{task.task_type}</TableCell>
                                <TableCell>{customTask ? JSON.stringify(task.messages) : task.prompt}</TableCell>
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
