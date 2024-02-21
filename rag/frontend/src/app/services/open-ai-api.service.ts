import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})

export class OpenAiApiService {
  private apiUrl = environment.apiUrl; // Update with your Node.js server URL

  constructor(private http: HttpClient) { }

  public sendMessage(chatHistory: { role: string, content: string, question?: string }[]) {
    return this.http.post<any>(`${this.apiUrl}/chat`, { chatHistory });
  }
}