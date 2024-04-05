'use client'
import React from 'react';
import {
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    TextField,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    Alert,
    Snackbar
} from '@mui/material';
import {useAppSelector} from "@/store";
import {gql} from '@apollo/client';
import {useQuery} from '@apollo/client';
import {llmCreateTask} from "@/cloud/utils/llm_create_task";


const GET_MODELS = gql`
    query GetModels {
        llm_llmconfigrecords {
                id
                model_name
        }
    }
`;


export default function MyFormDialog({open, onClose, onSubmit}) {

    const username = useAppSelector(state => state.auth.authState.username);
    const {
        data,
        // loading,
        // error
    } = useQuery(GET_MODELS);
    const [snackbar, setSnackbar] = React.useState({
        open: false,
        message: '',
        severity: 'success', // or 'error'
    });
    const [formData, setFormData] = React.useState({
        name: "",
        workType: 'gpu', // default to GPU
        prompt: '',
        modelName: 'llama2-13b-chat', // default model name
        llmTaskType: 'create_embedding', // default task type
    });

    const handleChange = (event) => {
        const {name, value} = event.target;
        setFormData(prevState => ({
            ...prevState,
            [name]: value,
        }));
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        // change camelCase to snake_case
        const requestData = {
            ...formData,
            model_name: formData.modelName,
            work_type: formData.workType,
            llm_task_type: formData.llmTaskType,
        };
        const resStatus = await llmCreateTask(requestData)
        if (resStatus) {
            setSnackbar({open: true, message: 'Request submitted successfully!', severity: 'success'});
            onClose(); // Optionally close the dialog
        } else {
            // Assume failure if resStatus isn't true
            setSnackbar({open: true, message: 'Failed to submit the request.', severity: 'error'});
        }

    };

    if (!data) {
        return null;
    }
    return (
        <>
            <Snackbar
                open={snackbar.open}
                autoHideDuration={6000}
                onClose={() => setSnackbar({...snackbar, open: false})}
                anchorOrigin={{vertical: 'bottom', horizontal: 'left'}}
            >
                <Alert onClose={() => setSnackbar({...snackbar, open: false})} severity={snackbar.severity}
                       sx={{width: '100%'}}>
                    {snackbar.message}
                </Alert>
            </Snackbar>
            <Dialog open={open} onClose={onClose}>
                <DialogTitle>Submit Your LLM Prompt Task</DialogTitle>
                <DialogContent>
                    <form onSubmit={handleSubmit}>
                        <FormControl fullWidth sx={{mt: 2, mb: 2}} variant="standard">
                            <TextField
                                name="name"
                                label="Name"
                                type="text"
                                fullWidth
                                required
                                variant="filled"
                                placeholder={username}
                                value={formData.name}
                                multiline
                                helperText="Name your request to identify and manage tasks later"
                                onChange={handleChange}
                                sx={{mb: 2}}
                            />
                        </FormControl>
                        <FormControl fullWidth sx={{mb: 2}} variant="standard">
                            <TextField
                                name="prompt"
                                label="Prompt"
                                type="text"
                                fullWidth
                                required
                                variant="filled"
                                value={formData.prompt}
                                multiline
                                rows={4}
                                onChange={handleChange}
                                sx={{mb: 2}} // Add more bottom margin
                            />
                        </FormControl>
                        <FormControl fullWidth sx={{mb: 2}} variant="standard"> {/* Add more bottom margin */}
                            <InputLabel id="model-name-label">Model Name</InputLabel>
                            <Select
                                labelId="model-name-label"
                                name="modelName"
                                value={formData.modelName}
                                label="Model Name"
                                onChange={handleChange}
                                variant='filled'
                            >
                                {data?.llm_llmconfigrecords.map((model) => (
                                    <MenuItem key={model.id} value={model.model_name}>{model.model_name}</MenuItem>
                                ))}
                                <MenuItem value="bert">sentence_transformers</MenuItem>
                                {/* Add other model options here */}
                            </Select>
                        </FormControl>
                        <FormControl fullWidth sx={{mb: 2}} variant="standard">
                            <InputLabel id="work-type-label">Work Type</InputLabel>
                            <Select
                                labelId="work-type-label"
                                name="workType"
                                value={formData.workType}
                                label="Work Type"
                                variant='filled'
                                onChange={handleChange}
                            >
                                <MenuItem value="gpu">GPU</MenuItem>
                                <MenuItem value="cpu">CPU</MenuItem>
                            </Select>
                        </FormControl>
                        <FormControl fullWidth sx={{mb: 2}}
                                     variant="standard"> {/* Add more bottom margin for the last item */}
                            <InputLabel id="llm-task-type-label">LLM Task Type</InputLabel>
                            <Select
                                labelId="llm-task-type-label"
                                name="llmTaskType"
                                value={formData.llmTaskType}
                                label="LLM Task Type"
                                variant='filled'
                                onChange={handleChange}
                            >
                                <MenuItem value="create_embedding">Create Embedding</MenuItem>
                                <MenuItem value="chat_completion">Chat Completion</MenuItem>
                                <MenuItem value="completion">Completion</MenuItem>
                            </Select>
                        </FormControl>
                    </form>
                    {/*    add a component to indicate result */}
                </DialogContent>
                <DialogActions>
                    <Button onClick={onClose}>Cancel</Button>
                    <Button onClick={handleSubmit} autoFocus>
                        Submit
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
}
