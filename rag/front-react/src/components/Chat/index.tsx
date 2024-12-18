import React from 'react';
import { Typography, Paper, Avatar, useTheme, CircularProgress } from '@mui/material';
import amaris from 'assets/images/amaris.jpg';
import knowledge from 'assets/images/books.jpg';
import ragybot from 'assets/images/logo192.png'
import { IMessage } from 'models/interfaces/IMessage';


const Chat: React.FC<IMessage> = ({ content, chatbot, role}) => {
    const theme = useTheme();

    return (
        <div style={{
            padding: theme.spacing(2),
            marginBottom: theme.spacing(2),
            maxWidth: '100%',
            display: 'flex',
            alignItems: 'center',
            }}>
            <Avatar alt="You" src={chatbot ? ragybot : (role === 'user' ? amaris : knowledge)} style={{ marginRight: theme.spacing(2) }} />
        <div>
            <Typography variant="h4">{chatbot ? "Ragybot.be" : "You"}</Typography>
            {content ? (
                <Typography>{content}</Typography>
            ) : (
                <CircularProgress size={15} thickness={4} />
            )}
        </div>
        </div>
    );
};

export default Chat;
