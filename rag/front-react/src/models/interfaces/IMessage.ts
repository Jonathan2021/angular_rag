export interface IMessage {
    chatbot: boolean;
    content?: string;
    role?: 'user' | 'assistant' | 'document';
    question?: string;
}
