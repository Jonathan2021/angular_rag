export interface IMessage {
    chatbot: boolean;
    text?: string;
    role?: 'user' | 'assistant' | 'document';
    question?: string;
}