'use client'
// pages/chat.tsx

import { useState, useRef, useEffect } from 'react';
import styles from '../styles/Chat.module.css';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'bot';
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const bottomRef = useRef<null | HTMLDivElement>(null);

  const sendMessage = (text: string) => {
    if (!text.trim()) return;
    setMessages((prevMessages) => [
      ...prevMessages,
      { id: Date.now(), text: text.trim(), sender: 'user' },
    ]);
    // Simulate bot response
    setTimeout(() => {
      setMessages((prevMessages) => [
        ...prevMessages,
        { id: Date.now(), text: `Echo: ${text.trim()}`, sender: 'bot' },
      ]);
    }, 500);
    setInputText('');
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => setInputText(e.target.value);

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(inputText);
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className={styles.chatContainer}>
      <div className={styles.messagesContainer}>
        {messages.map((message) => (
          <div key={message.id} className={`${styles.message} ${message.sender === 'user' ? styles.user : styles.bot}`}>
            {message.text}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <form onSubmit={handleFormSubmit} className={styles.messageForm}>
        <input
          type="text"
          value={inputText}
          onChange={handleInputChange}
          placeholder="Type your message here..."
          className={styles.inputField}
        />
        <button type="submit" className={styles.sendButton}>Send</button>
      </form>
    </div>
  );
}
