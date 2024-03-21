import React, { useEffect, useRef, useState } from 'react';
import logoImage from 'assets/images/logo.png';
import { TextField, Container, Typography, Box, IconButton } from '@mui/material';
import Send from '@mui/icons-material/Send';
import Chat from 'components/Chat';
import styles from './styles';
import { IMessage } from 'models/interfaces/IMessage';
import { useApi } from 'hooks/useApi';

interface Document {
  title: string;
  content: string;
}

interface ResponseRAG {
  documents: Document[];
  reply: string;
}

const ChatView: React.FC = () => {
  const [messages, setMessages] = useState<IMessage[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>();
  const [inputText, setInputText] = useState<string>('');
  const { post } = useApi();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleMessageSend = async () => {
    if (inputText.trim() !== '') {
      setInputText('');
      setIsLoading(true);
      setError(undefined); // Clear any existing errors
      
      const newUserMessage : IMessage = { chatbot: false, content: inputText, role: 'user' };
      const newMessages = [...messages, newUserMessage]
      setMessages(prevMessages => [...prevMessages, newUserMessage]);

      
      // LE SETTIMEOUT EST POUR TEST LE FRONT UNIQUEMENT
      /*setTimeout(() => {
        const responseText = getRandomResponse(); // Obtenir un message aléatoire
        setMessages(prevMessages => [...prevMessages, { chatbot: true, text: responseText }]);
        setIsLoading(false)
        }, 1000);*/
      
      // FONCTION POUR APPELLER LE BACK ROBOT
      try {
        // Envoi de la requête à l'API
        const response = await post<ResponseRAG>('chat', {chatHistory: newMessages});
  
        // Gestion de la réponse de l'API
        setIsLoading(false); // Définit isLoading à false après la réponse
        if (response.documents && response.documents.length > 0) {
          // Si des documents sont retournés par l'API, les traiter et les ajouter aux messages
          response.documents.forEach((doc) => {
            const docMessageObject: IMessage = { role: 'document', chatbot: false, content: doc.content };
            setMessages(prevMessages => [...prevMessages, docMessageObject]); // Ajoute le message du document à la liste des messages
          });
        }
        // Ajoute la réponse de l'assistant à la liste des messages
        const assistantMessageObject: IMessage = { role: 'assistant', chatbot: true, content: response.reply, question: inputText };
        setMessages(prevMessages => [...prevMessages, assistantMessageObject]);
        
        // Effectue le défilement vers le bas de la fenêtre de chat
        setTimeout(() => scrollToBottom(), 0);
      } catch (error) {
        console.error('Error sending message:', error);
        setError("Error server, please try again later.")
      }
    }
  };

  // Fonction pour obtenir un message aléatoire de réponse
  const getRandomResponse = (): string => {
    const responses = [
      "Bonjour! Comment puis-je vous aider?",
      "Je suis là pour répondre à vos questions. Que puis-je faire pour vous?",
      "Dites-moi ce que vous avez besoin, je suis prêt à vous aider!",
      "Je suis un robot amical, prêt à résoudre tous vos problèmes!",
      "N'hésitez pas à me demander quoi que ce soit!",
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  };

  return (
    <Container maxWidth="xl" sx={styles.globalContainerStyles}>
      <img src={logoImage} alt="Logo" style={{ height: 80 }} />
      {messages.length ? (
        <Box flex={1} sx={styles.chatContainerStyles}>
          {/* HAVING CHATS */}
          {messages.map((message) => (
            <Chat content={message.content} chatbot={message.chatbot} role={message.role}/>
          ))}
          {isLoading && (
            <Chat chatbot={true} content={error ? error : undefined} />
          )}
          <div ref={messagesEndRef} />
        </Box>
      ) : (
        <>
          {/* NO CHATS */}
          <Box display={"flex"} flex={2} alignItems={"center"} justifyContent="center">
            <Typography variant="h3">How can I help you today?</Typography>
          </Box>
          <Box flex={1} />
        </>
      )}
      <Container sx={styles.footerStyles}>
        <TextField
          fullWidth
          label="Message Ragybot.BE"
          variant="outlined"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          inputProps={{ maxLength: 200 }}
          onKeyDown={(e) => e.key === 'Enter' && handleMessageSend()}
          InputProps={{
            endAdornment: (
              <IconButton color="primary" onClick={handleMessageSend}>
                <Send />
              </IconButton>
            )
          }}
        />
        <Typography variant='body2'>Ragybot.be cannot make mistakes. Consider it's a boss.</Typography>
      </Container>
    </Container>
  );  
};

export default ChatView;
