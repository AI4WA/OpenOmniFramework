'use client'

import React, {useState, useRef, useEffect} from 'react';
import {
    Box,
    IconButton,
    Grid,
    Typography,
    List,
    Container,
    ListItem,
    Divider,
    InputBase,
    ListItemText,
    MenuItem,
    Select,
    InputLabel,
    FormControl
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import Header from "@/components/Header";
import useMediaQuery from "@mui/material/useMediaQuery";
import {useTheme} from "@mui/material/styles";
import {useSubscription, useMutation, useQuery, gql} from "@apollo/client";
import {useAppSelector} from "@/store";
import AddIcon from '@mui/icons-material/Add';
import {v4 as uuidv4} from 'uuid';
import {SelectChangeEvent} from '@mui/material/Select';

const CHAT_QUERY = gql`
subscription Chat($userId: bigint!) {
  chat_chat(where: {user_id: {_eq: $userId}}, order_by: {created_at: desc}) {
    uuid
    llm_model_name
    summary
    id
    chat_chatrecords_aggregate {
      aggregate {
        count
      }
    }
  }
}
`

const CHAT_MESSAGES = gql`
subscription ChatMessages($chatId: bigint!) {
  chat_chat(where: {id: {_eq: $chatId}}) {
    chat_chatrecords(order_by: {created_at: asc}) {
      id
      message
      role
      created_at
    }
    llm_model_name
    summary
    uuid
  }
}
`

const ADD_CHAT = gql`
mutation CreateChat($uuid: uuid!, $llmModelName: String!, $userId: bigint!) {
  insert_chat_chat_one(object: {user_id: $userId,
  llm_model_name: $llmModelName, uuid: $uuid, created_at: "now()", updated_at: "now()"}) {
    id
  }
}
`

const GET_MODELS = gql`
    query GetModels {
        llm_llmconfigrecords {
                id
                model_name
        }
    }
`;


const ADD_CHAT_MESSAGE = gql`
mutation AddChatMessage($chatId: bigint!, $message: String!, $role: String!){
  insert_chat_chatrecord_one(object: {chat_id: $chatId,
                                      message: $message,
                                      role: $role,
                                      created_at: "now()",
                                      updated_at: "now()"}) {
    id
  }
}
`

const UPDATE_CHAT = gql`
mutation UpdateChat($chatId: bigint!, $llmModelName: String!) {
  update_chat_chat(where: {id: {_eq: $chatId}}, _set: {llm_model_name: $llmModelName, updated_at: "now()"}) {
    affected_rows
  }
}
`

interface MessagesProp {
    chatId: number | null
}

interface ChatMessage {
    id: number,
    message: string,
    role: string,
    created_at: string
}

interface ChatProps {
    id: number,
    llm_model_name: string,
    summary: string,
    uuid: string,
    chat_chatrecords: ChatMessage[]
}

interface ModelProps {
    id: number,
    model_name: string
}

const Messages: React.FC<MessagesProp> = ({chatId}) => {
    const {data: chatMessage} = useSubscription(CHAT_MESSAGES, {
        variables: {chatId}
    });
    const messagesEndRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        // Auto-scroll to the latest message
        messagesEndRef?.current?.scrollIntoView({behavior: 'smooth'});
    }, [chatMessage]);

    return (
        <List>
            {chatMessage?.chat_chat?.[0].chat_chatrecords?.map((message: ChatMessage) => (
                <ListItem key={message.id}>
                    <Box
                        sx={{
                            background: message.role === 'assistant' ? '#f0f0f0' : '#e3f2fd',
                            borderRadius: '15px',
                            p: 2,
                            maxWidth: '85%',
                            marginLeft: message.role === 'assistant' ? 0 : 'auto',
                        }}
                    >
                        <Typography variant="body1">{message.message}</Typography>
                    </Box>
                </ListItem>
            ))}
            <div ref={messagesEndRef}/>
        </List>
    );
}


const ChatGPTApp = () => {
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
    const userId = useAppSelector(state => state.auth.authState?.userId);
    const [inputMessage, setInputMessage] = useState('');
    const [selectedModel, setSelectedModel] = useState('llama2-13b-chat');
    const [currentChatId, setCurrentChatId] = useState<number | null>(null);
    const [chatHistory, setChatHistory] = useState([]);

    const [addChat] = useMutation(ADD_CHAT);
    const [addChatMessage] = useMutation(ADD_CHAT_MESSAGE);
    const [updateChat] = useMutation(UPDATE_CHAT);

    const {data: chatData} = useSubscription(CHAT_QUERY, {
        variables: {userId: userId}
    });

    const {data: modelsData} = useQuery(GET_MODELS);

    const handleAddChat = async () => {
        const uuid = uuidv4();
        const res = await addChat({
            variables: {
                uuid: uuid,
                llmModelName: selectedModel,
                userId: userId
            }
        });
        if (res.data) {
            setCurrentChatId(res.data.insert_chat_chat_one.id);
        }
    };

    const changeCurrentChat = (chatId: number) => {
        setCurrentChatId(chatId)
    }
    const handleSendMessage = async () => {
        if (!inputMessage.trim()) return;

        // if the current chat records count is 0, update it with current selected model
        if (chatData && chatData.chat_chat.find((chat: ChatProps) => chat.id === currentChatId)?.chat_chatrecords_aggregate.aggregate.count === 0) {
            await updateChat({
                variables: {
                    chatId: currentChatId,
                    llmModelName: selectedModel
                }
            });
        }
        await addChatMessage({
            variables: {
                chatId: currentChatId,
                message: inputMessage,
                role: 'user'
            }
        });

        setInputMessage('')
    };

    const handleModelChange = (event: SelectChangeEvent<string>) => {
        setSelectedModel(event.target.value);
    };

    useEffect(() => {
        // Load chat history, this one should be one off
        if (chatData) {
            setChatHistory(chatData.chat_chat);
            if (currentChatId === null) {
                setCurrentChatId(chatData.chat_chat[0]?.id || null);
            }
        }
    }, [chatData, currentChatId, setCurrentChatId]);

    useEffect(() => {
        if (currentChatId) {
            setSelectedModel(chatData.chat_chat.find((chat: ChatProps) => chat.id === currentChatId)?.llm_model_name);
        }
    }, [currentChatId, setSelectedModel, chatData]);


    return (
        <div>
            <Header/>
            <Container maxWidth="md" sx={{mt: 4}}>
                <Grid container spacing={2}>
                    {
                        !isMobile &&
                        <Grid item xs={12} md={3} lg={3}>
                            <Box sx={{overflowY: 'auto', height: '100%', pr: 2, borderRight: '1px solid #e0e0e0'}}>
                                <Box sx={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'space-between',
                                    pr: 2
                                }}>
                                    {/* Use a Box to wrap Typography if alignment needs adjustment */}
                                    <Box sx={{display: 'flex', alignItems: 'center', height: '100%'}}>
                                        <Typography variant="h6" gutterBottom sx={{lineHeight: 1, marginBottom: 0}}>
                                            History
                                        </Typography>
                                    </Box>
                                    <IconButton aria-label="add" size="small" onClick={handleAddChat}>
                                        <AddIcon fontSize="inherit"/>
                                    </IconButton>
                                </Box>
                                <List>
                                    {chatHistory.map((history: ChatProps) => (
                                        <ListItem key={history.id} selected={currentChatId === history.id}
                                                  onClick={() => changeCurrentChat(history.id)}>
                                            <ListItemText primary={history.summary || "..."}/>
                                        </ListItem>
                                    ))}
                                </List>
                            </Box>
                        </Grid>
                    }
                    <Grid item xs={12} md={8} lg={9}>
                        <Typography variant="h4" gutterBottom align="center">
                            Open Source LLM Chat
                        </Typography>
                        <Box
                            sx={{
                                height: '73vh',
                                overflow: 'auto',
                                mb: 2,
                                border: '1px solid #e0e0e0',
                                borderRadius: '5px',
                            }}
                        >
                            <List>
                                <ListItem>
                                    <FormControl fullWidth>
                                        <InputLabel id="model-select-label">Choose Model</InputLabel>
                                        <Select
                                            labelId="model-select-label"
                                            id="model-select"
                                            value={selectedModel}
                                            label="Choose Model"
                                            onChange={handleModelChange}
                                            disabled={
                                                chatData &&
                                                chatData.chat_chat.find((chat: ChatProps) => chat.id === currentChatId)?.chat_chatrecords_aggregate.aggregate.count > 0
                                            }
                                        >
                                            {modelsData &&
                                                modelsData?.llm_llmconfigrecords.map((model: ModelProps) => (
                                                    <MenuItem key={model.id}
                                                              value={model.model_name}>{model.model_name}</MenuItem>
                                                ))
                                            }
                                        </Select>
                                    </FormControl>
                                </ListItem>
                            </List>
                            <Messages chatId={currentChatId}/>
                        </Box>
                        <Box
                            component="form"
                            sx={{
                                display: 'flex',
                                alignItems: 'center',
                                border: '1px solid #e0e0e0',
                                borderRadius: '5px',
                            }}
                            onSubmit={async (e) => {
                                e.preventDefault();
                                await handleSendMessage()
                            }}

                        >
                            <InputBase
                                sx={{ml: 1, flex: 1}}
                                placeholder="Type your message here..."
                                value={inputMessage}
                                onChange={(e) => setInputMessage(e.target.value)}
                                fullWidth
                            />
                            <IconButton color="primary" type="submit">
                                <SendIcon/>
                            </IconButton>
                            <Divider/>
                        </Box>
                        <Box sx={{display: 'flex', justifyContent: 'center', mt: 1}}>
                            <Typography variant="caption" color="textSecondary">
                                Note: This is for Research Purposes Only
                            </Typography>
                        </Box>
                    </Grid>
                </Grid>
            </Container>
            {!isMobile &&
                <Box component="footer" sx={{
                    position: 'absolute',
                    bottom: 0,
                    left: 0,
                    right: 0,
                    p: 0,
                    backgroundColor: 'background.paper',
                    width: '100%'
                }}>
                    <footer className="bg-gray-800 text-white text-center p-4">
                        <p>Developed by
                            <a href="https://www.linkedin.com/in/pascalsun23/" target="_blank" rel="noopener noreferrer"
                               className="text-blue-400 hover:text-blue-300 mx-1">
                                Pascal Sun
                            </a>
                            supported by
                            <a href="https://nlp-tlp.org/" target="_blank" rel="noopener noreferrer"
                               className="text-blue-400 hover:text-blue-300 mx-1">
                                UWA NLP-TLP GROUP
                            </a>
                        </p>
                    </footer>
                </Box>
            }
        </div>
    );
};

export default ChatGPTApp;
