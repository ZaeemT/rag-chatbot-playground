import { useState, useEffect, useRef } from 'react'
import { Send } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ModeToggle } from './mode-toggle'
import { sendMessageToChatbot } from '@/services/chatbot.service'

type Message = {
    id: number
    text: string
    sender: 'user' | 'bot'
}

export default function ChatbotUI() {
    const [messages, setMessages] = useState<Message[]>([
        { id: 1, text: "Hello! How can I assist you today?", sender: 'bot' }
    ])
    const [input, setInput] = useState('')
    const [isTyping, setIsTyping] = useState(false)
    const scrollAreaRef = useRef<HTMLDivElement>(null)
    const endOfMessagesRef = useRef<HTMLDivElement>(null)

    const formatMessage = (message: string) => {
        // Split the message into lines
        const lines = message.split('\n');
    
        return (
            <div>
                {lines.map((line, index) => {
                    // Check if the line starts with a dash for bullet points
                    if (line.trim().startsWith('-')) {
                        return (
                            <ul key={index} className="list-disc ml-5">
                                <li>{applyBoldFormatting(line.slice(1).trim())}</li> {/* Remove dash and trim */}
                            </ul>
                        );
                    }
                    
                    // Otherwise, just apply bold formatting
                    return (
                        <p key={index}>
                            {applyBoldFormatting(line)}
                        </p>
                    );
                })}
            </div>
        );
    };
    
    // Helper function to apply bold formatting to text between **
    const applyBoldFormatting = (text: string) => {
        const boldRegex = /\*\*(.*?)\*\*/g; // Matches text between **
        const parts = text.split(boldRegex);
    
        return parts.map((part, index) => {
            if (index % 2 === 1) {
                // Odd index matches are the bold parts
                return <strong key={index}>{part}</strong>;
            }
            // Even index matches are normal text
            return <span key={index}>{part}</span>;
        });
    };
    


    const handleSend = async () => {
        if (input.trim()) {
            const newMessage: Message = { id: messages.length + 1, text: input, sender: 'user' }
            setMessages([...messages, newMessage])
            setInput('')
            setIsTyping(true)
    
            try {
                const botReply = await sendMessageToChatbot(input);
    
                const botResponse: Message = { id: messages.length + 2, text: botReply, sender: 'bot' }
                
                setMessages(prevMessages => [...prevMessages, botResponse]);
            } catch (error) {
                console.error("Failed to get bot response:", error);
                const errorMessage: Message = { id: messages.length + 2, text: "Something went wrong. Please try again.", sender: 'bot' }
                setMessages(prevMessages => [...prevMessages, errorMessage]);
            } finally {
                setIsTyping(false);
            }
        }
    }
    

    useEffect(() => {
        // Scroll to bottom of message list when new messages are added
        endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    return (
        <div className="flex flex-col h-screen w-full bg-background">
            <header className="flex items-center justify-center h-16 p-4 bg-primary text-primary-foreground">
                <h1 className="text-2xl font-bold">Chatbot</h1>
                <div className="ml-auto">
                    <ModeToggle />
                </div>
            </header>
            <main className="flex-grow overflow-hidden">
                <ScrollArea ref={scrollAreaRef} className="h-full p-4">
                    <div className="space-y-4 max-w-3xl mx-auto">
                        {messages.map((message) => (
                            <div
                                key={message.id}
                                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div
                                    className={`max-w-[70%] rounded-lg p-3 ${message.sender === 'user'
                                        ? 'bg-primary text-primary-foreground'
                                        : 'bg-secondary text-secondary-foreground'
                                        }`}
                                >
                                    {formatMessage(message.text)}
                                </div>
                            </div>
                        ))}
                        {isTyping && (
                            <div className="flex justify-start">
                                <div className="bg-secondary text-secondary-foreground max-w-[70%] rounded-lg p-3">
                                    <div className="flex space-x-2">
                                        <div className="w-3 h-3 rounded-full bg-gray-500 animate-bounce"></div>
                                        <div className="w-3 h-3 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                        <div className="w-3 h-3 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={endOfMessagesRef} /> 
                    </div>
                </ScrollArea>
            </main>
            <footer className="p-4 border-t">
                <div className="flex space-x-2 max-w-3xl mx-auto">
                    <Input
                        type="text"
                        placeholder="Type your message..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                        className="flex-grow"
                    />
                    <Button onClick={handleSend} className="px-4">
                        <Send className="h-4 w-4" />
                        <span className="sr-only">Send message</span>
                    </Button>
                </div>
            </footer>
        </div>
    )
}