'use client'
import React, {useState} from 'react';
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
    Snackbar,
    Checkbox,
    FormGroup,
    FormControlLabel,
    AlertColor,
    IconButton,
    Box
} from '@mui/material';
import {useAppSelector} from "@/store";
import {gql} from '@apollo/client';
import {useQuery} from '@apollo/client';
import {llmCreateTask, llmCustomCreateTask} from "@/cloud/utils/llm_create_task";
import {SelectChangeEvent} from '@mui/material/Select';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import RemoveCircleOutlineIcon from '@mui/icons-material/RemoveCircleOutline';

import LLMTaskAddFile from "@/components/LLMTaskAddFile";

const GET_MODELS = gql`
    query GetModels {
        llm_llmconfigrecords {
                id
                model_name
        }
    }
`;

interface MyFormDialogProps {
    open: boolean;
    onClose: () => void; // Assuming onClose doesn't expect any argument
}

interface SnackbarState {
    open: boolean;
    message: string;
    severity: AlertColor; // Use AlertColor type here
}

interface LLMConfigModel {
    id: number;
    model_name: string;
}

interface Message {
    role: "system" | "user" | "assistant" | "function";
    content: string;
}

interface FormData {
    name: string;
    workType: string;
    prompt: string;
    messages: Message[];
    modelName: string;
    llmTaskType: string;
}

const MyFormDialog: React.FC<MyFormDialogProps> = ({open, onClose}) => {
    const messageTypes = ['system', 'user', 'assistant', 'function'];
    const username = useAppSelector(state => state.auth.authState.username);
    const {
        data,
        // loading,
        // error
    } = useQuery(GET_MODELS);
    const [snackbar, setSnackbar] = React.useState<SnackbarState>({
        open: false,
        message: '',
        severity: 'success', // or 'error'
    });
    const [formData, setFormData] = React.useState<FormData>({
        name: "",
        workType: 'gpu', // default to GPU
        prompt: '',
        messages: [],
        modelName: 'llama2-13b-chat', // default model name
        llmTaskType: 'create_embedding', // default task type
    });
    const [isAdvanced, setIsAdvanced] = useState(false);
    const [useCsvImport, setUseCsvImport] = useState(false);

    const handleChange = (event: React.ChangeEvent<HTMLInputElement> | React.ChangeEvent<HTMLTextAreaElement | HTMLInputElement> | SelectChangeEvent) => {
        // Assuming all inputs/selects have 'name' and 'value' attributes
        const name = (event.target as HTMLInputElement).name;
        const value = (event as React.ChangeEvent<HTMLInputElement>).target.value || (event as SelectChangeEvent).target.value;

        setFormData((prevState) => ({
            ...prevState,
            [name]: value,
        }));
    };

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        let resStatus: boolean;
        console.log(formData.messages)
        if (isAdvanced) {

            const requestData = {
                ...formData,
                messages: formData.messages,
                model_name: formData.modelName,
                task_type: formData.workType,
                llm_task_type: formData.llmTaskType,
            };

            resStatus = await llmCustomCreateTask(requestData);
        } else {
            // Assuming formData is correctly structured and llmCreateTask expects such structure
            const requestData = {
                ...formData,
                model_name: formData.modelName,
                task_type: formData.workType,
                llm_task_type: formData.llmTaskType,
            };

            resStatus = await llmCreateTask(requestData);
        }

        if (resStatus) {
            setSnackbar({open: true, message: 'Request submitted successfully!', severity: 'success'});
            onClose(); // Close the dialog
        } else {
            // Handle submission failure
            setSnackbar({open: true, message: 'Failed to submit the request.', severity: 'error'});
        }
    };

    const handleCheckboxChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setIsAdvanced(event.target.checked);
    };

    const handleAddMessage = () => {
        setFormData((prevState: FormData) => ({
            ...prevState,
            messages: [...prevState.messages, {role: 'system', content: ''}],
        }));
    };

    const handleRemoveMessage = (index: number) => {
        setFormData((prevState: FormData) => ({
            ...prevState,
            messages: prevState.messages.filter((_, i) => i !== index),
        }));
    };

    const handleChangeMessage = (index: number, field: keyof Message, value: string) => {
        setFormData((prevState: FormData) => ({
            ...prevState,
            messages: prevState.messages.map((message, i) => {
                if (i === index) {
                    return {
                        ...message,
                        [field]: value,
                    };
                }
                return message;
            }),
        }));
    };

    const handleCsvCheckboxChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setUseCsvImport(event.target.checked);
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
                <DialogTitle
                    // mb 0
                    sx={{pb: 0, mb: 0}}
                >Submit Your LLM Prompt Task
                    <FormGroup row>
                        <FormControlLabel
                            control={
                                <Checkbox
                                    checked={useCsvImport}
                                    onChange={handleCsvCheckboxChange}
                                    name="useCsvImport"
                                />
                            }
                            label="Batch Submit file import"
                        />
                    </FormGroup>
                </DialogTitle>
                {
                    useCsvImport ? (
                        <>
                            <DialogContent>
                                <LLMTaskAddFile
                                    setSnackbar={setSnackbar}/>
                            </DialogContent>
                            <DialogActions>
                                <Button onClick={onClose}>Cancel</Button>
                            </DialogActions>
                        </>

                    ) : (
                        <div>
                            <form onSubmit={handleSubmit}>
                                <DialogContent>
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
                                    <FormGroup>
                                        <FormControlLabel
                                            control={<Checkbox checked={isAdvanced} onChange={handleCheckboxChange}/>}
                                            label="Use Advanced Settings"
                                        />
                                    </FormGroup>

                                    {!isAdvanced ? (
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
                                                sx={{mb: 2}}
                                            />
                                        </FormControl>
                                    ) : (
                                        <div>
                                            {formData.messages.map((message: Message, index) => (
                                                <Box
                                                    key={index}
                                                    sx={{
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        marginBottom: '10px',
                                                    }}
                                                >
                                                    <FormControl fullWidth sx={{mr: 1}}>
                                                        <InputLabel>Role</InputLabel>
                                                        <Select
                                                            value={message.role}
                                                            label="Role"
                                                            onChange={(e) => handleChangeMessage(index, 'role', e.target.value)}
                                                        >
                                                            {messageTypes.map((type) => (
                                                                <MenuItem key={type} value={type}>
                                                                    {type.charAt(0).toUpperCase() + type.slice(1)}
                                                                </MenuItem>
                                                            ))}
                                                        </Select>
                                                    </FormControl>
                                                    <FormControl fullWidth sx={{mx: 1}}>
                                                        <TextField
                                                            label="Content"
                                                            type="text"
                                                            variant="filled"
                                                            value={message.content}
                                                            onChange={(e) => handleChangeMessage(index, 'content', e.target.value)}
                                                        />
                                                    </FormControl>
                                                    {index > 0 && (
                                                        <IconButton onClick={() => handleRemoveMessage(index)}>
                                                            <RemoveCircleOutlineIcon/>
                                                        </IconButton>
                                                    )}
                                                </Box>
                                            ))}
                                            <Button startIcon={<AddCircleOutlineIcon/>} onClick={handleAddMessage}>
                                                Add Message
                                            </Button>
                                        </div>
                                    )}
                                    <FormControl fullWidth sx={{mb: 2}}
                                                 variant="standard"> {/* Add more bottom margin */}
                                        <InputLabel id="model-name-label">Model Name</InputLabel>
                                        <Select
                                            labelId="model-name-label"
                                            name="modelName"
                                            value={formData.modelName}
                                            label="Model Name"
                                            onChange={handleChange}
                                            variant='filled'
                                        >
                                            {data?.llm_llmconfigrecords.map((model: LLMConfigModel) => (
                                                <MenuItem key={model.id}
                                                          value={model.model_name}>{model.model_name}</MenuItem>
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
                                </DialogContent>
                                <DialogActions>
                                    <Button onClick={onClose}>Cancel</Button>
                                    <Button type="submit" autoFocus>
                                        Submit
                                    </Button>
                                </DialogActions>
                            </form>
                        </div>
                    )
                }
            </Dialog>
        </>
    );
}


export default MyFormDialog