'use client'
import React, {useState, useRef, useEffect} from 'react';
import {
    Box,
    IconButton,
    TextField,
    AppBar,
    Toolbar,
    Typography,
    List,
    Container,
    ListItem,
    ListItemText,
    Divider,
    Paper,
    InputBase,
    Grid
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import Header from "@/components/Header";


const ChatPage = () => {
    const [messages, setMessages] = useState([]);
    const [currentMessage, setCurrentMessage] = useState('');
    const [chatHistory, setChatHistory] = useState([
        {id: 1, title: "Session 1"},
        {id: 2, title: "Session 2"},
        {id: 3, title: "Session 3"},
        // Add more chat sessions as needed
    ]);
    const messagesEndRef = useRef(null);
    const handleSendMessage = () => {
        if (!currentMessage.trim()) return;
        const newMessage = {id: Date.now(), text: currentMessage, sender: 'user'};
        setMessages((prevMessages) => [...prevMessages, newMessage]);
        setCurrentMessage('');

        // Simulate a bot response
        setTimeout(() => {
            const botResponse = {id: Date.now(), text: `Echo: ${currentMessage}`, sender: 'bot'};
            setMessages((prevMessages) => [...prevMessages, botResponse]);
        }, 500);
    };

    const handleMessageChange = (event) => {
        setCurrentMessage(event.target.value);
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleSendMessage();
        }
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({behavior: "smooth"});
    };

    useEffect(() => {
        // Scroll to bottom every time messages update
        scrollToBottom();
    }, [messages]);


    return (

        <Box sx={{
            flexGrow: 1,
            display: 'flex',
            flexDirection: 'column',
            height: '100vh',
            backgroundColor: "white",
            overflow: 'hidden',
        }}>
            <Header/>
            <Grid container
                  sx={{flexGrow: 1, height: 'calc(100vh - 64px)'}}> {/* Adjust height based on AppBar height */}
                <Grid item xs={12} sm={4} md={3} lg={2} sx={{borderRight: 1, borderColor: 'divider'}}>
                    <List sx={{overflow: 'auto', height: '100%'}}>
                        {chatHistory.map((session) => (
                            <ListItem button key={session.id}>
                                <ListItemText primary={session.title}/>
                            </ListItem>
                        ))}
                    </List>
                </Grid>
                <Grid item xs={12} sm={8} md={9} lg={10}
                      sx={{display: 'flex', flexDirection: 'column', height: '100%'}}>
                    <List sx={{overflow: 'auto', flexGrow: 1, maxHeight: 'calc(100vh - 64px - 56px)'}}>
                        {messages.map((message) => (
                            <ListItem key={message.id}>
                                <ListItemText
                                    primary={message.text}
                                    secondary={message.sender === 'bot' ? 'Chatbot' : 'You'}
                                />
                            </ListItem>
                        ))}
                        {/* Ref at the end of messages to scroll into view */}
                        <div ref={messagesEndRef}/>
                    </List>
                    <Divider/>
                    <Paper
                        component="form"
                        sx={{p: '2px 4px', display: 'flex', alignItems: 'end'}}
                        onSubmit={handleSendMessage}
                    >
                        <InputBase
                            sx={{ml: 1, flex: 1}}
                            placeholder="Type your message here..."
                            value={currentMessage}
                            onChange={handleMessageChange}
                        />
                        <IconButton color="primary" sx={{p: '10px'}} aria-label="send" onClick={handleSendMessage}>
                            <SendIcon/>
                        </IconButton>
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
};

export default ChatPage;
