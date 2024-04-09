'use client'
// ChatGPTApp.js
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
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import Header from "@/components/Header";
import useMediaQuery from "@mui/material/useMediaQuery";
import {useTheme} from "@mui/material/styles";

const ChatGPTApp = () => {
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const messagesEndRef = useRef(null);
    const [chatHistory, setChatHistory] = useState([
        {id: 1, title: "Chat 1"},
        {id: 2, title: "Chat 2"},
        // Add more chat history items here
    ]);
    const handleSendMessage = async () => {
        if (!inputMessage.trim()) return;

        const userMessage = {
            id: Date.now(),
            text: inputMessage,
            sender: 'user'
        };

        setMessages((prevMessages) => [...prevMessages, userMessage]);
        setInputMessage('');

        // Placeholder for sending inputMessage to the ChatGPT backend and receiving a response
        const botResponse = {
            id: Date.now() + 1, // Ensure unique ID
            text: `AI Response to: "${inputMessage}"`, // Placeholder for actual AI response
            sender: 'bot'
        };

        setTimeout(() => {
            setMessages((prevMessages) => [...prevMessages, botResponse]);
        }, 500); // Simulate network request delay
    };

    useEffect(() => {
        // Auto-scroll to the latest message
        messagesEndRef.current?.scrollIntoView({behavior: 'smooth'});
    }, [messages]);

    return (
        <div>
            <Header/>

            <Container maxWidth="md" sx={{mt: 4}}>
                <Grid container spacing={2}>
                    {/* Chat history sidebar */}
                    {
                        !isMobile &&
                        <Grid item xs={12} md={3} lg={3}>
                            <Box sx={{overflowY: 'auto', height: '100%', pr: 2, borderRight: '1px solid #e0e0e0'}}>
                                <Typography variant="h6" gutterBottom>
                                    Chat History
                                </Typography>
                                <List>
                                    {chatHistory.map((history) => (
                                        <ListItem button key={history.id}>
                                            <ListItemText primary={history.title}/>
                                        </ListItem>
                                    ))}
                                </List>
                            </Box>
                        </Grid>
                    }


                    {/* Current chat session */}
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
                                {messages.map((message) => (
                                    <ListItem key={message.id}>
                                        <Box
                                            sx={{
                                                background: message.sender === 'bot' ? '#f0f0f0' : '#e3f2fd',
                                                borderRadius: '15px',
                                                p: 2,
                                                maxWidth: '85%',
                                                marginLeft: message.sender === 'bot' ? 0 : 'auto',
                                            }}
                                        >
                                            <Typography variant="body1">{message.text}</Typography>
                                        </Box>
                                    </ListItem>
                                ))}
                                <div ref={messagesEndRef}/>
                            </List>
                        </Box>
                        <Box
                            component="form"
                            sx={{
                                display: 'flex',
                                alignItems: 'center',
                            }}
                            onSubmit={(e) => {
                                e.preventDefault();
                                handleSendMessage();
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
                            {/*    add for research only small text under it*/}

                        </Box>
                        <Box sx={{display: 'flex', justifyContent: 'center', mt: 1}}>
                            <Typography variant="caption" color="textSecondary">
                                Note: This is for Research Purposes Only
                            </Typography>
                        </Box>
                    </Grid>
                </Grid>
            </Container>
            {/*if it is mobile, do not absolute */}

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
