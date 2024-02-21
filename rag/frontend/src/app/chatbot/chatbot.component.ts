import { Component } from '@angular/core';
import { OpenAiApiService } from '../services/open-ai-api.service';

@Component({
  selector: 'app-chatbot',
  templateUrl: './chatbot.component.html',
  styleUrls: ['./chatbot.component.css']
})

export class ChatbotComponent {
  userMessage!: string;
  assistantReply!: string;
  chatMessages: { role: string, content: string, question?: string }[] = [];
  documents: { title: string, content: string }[] = [];  // Array to store documents
  formatDocumentForDisplay(doc : { title: string, content: string }): string {
    return `<strong>Document Title:</strong> ${doc.title}<br><strong>Content:</strong> ${doc.content}`;
  }

  constructor(private openAiApiService: OpenAiApiService){}

  sendMessage() {
    const userMessage = this.userMessage;
    this.chatMessages.push({ role: 'user', content: userMessage });
    this.openAiApiService.sendMessage(this.chatMessages)
    .subscribe(response => {
      // Handle documents
      if (response.documents && response.documents.length > 0) {
        this.documents = response.documents;
        response.documents.forEach((doc: { title: string, content: string }) => {
          this.chatMessages.push({ role: 'document', content: this.formatDocumentForDisplay(doc) });
        });
      }
      this.assistantReply = response.reply;
      this.chatMessages.push({ role: 'assistant', content: this.assistantReply, question: userMessage });
      this.userMessage = '';
    });
  }
}