import { POST } from './api.service.wrapper'; // Import the POST method from the wrapper
import { apiUrl } from '../utils/constants';

// Define the interface for the response from the chatbot
interface ChatbotResponse {
  answer: string;
}

// Function to send a message to the chatbot API
export const sendMessageToChatbot = async (query: string): Promise<string> => {
  try {
    // Use the POST method to send the query to the chatbot API
    const response = await POST<ChatbotResponse>(apiUrl.chatbot, { query });

    // Return the answer from the chatbot API response
    return response.answer;
  } catch (error) {
    console.error('Error sending message to chatbot:', error);
    throw new Error('Failed to get chatbot response');
  }
};
