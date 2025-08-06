import React, { useState, useRef, useEffect } from 'react';
import { 
  MessageCircle, 
  Send, 
  Bot, 
  User, 
  Loader2,
  Lightbulb,
  Clock,
  CheckCircle
} from 'lucide-react';

import { InvoiceChainApi, handleApiError } from '@/services/api';
import type { ChatMessage } from '@/types';
import { cn, generateId } from '@/lib/utils';

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: generateId(),
      type: 'agent',
      content: `👋 Hello! I'm your Invoice Chain Agent assistant. I can help you with:

• **Check invoice status**: "What's the status of invoice INV-001?"
• **Risk analysis**: "What's the fraud risk for invoice INV-001?"
• **System statistics**: "Show me system statistics"
• **Recent activity**: "Show me recent invoices"

What would you like to know?`,
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const examplePrompts = [
    "What's the risk of invoice INV-001?",
    "Check invoice INV-001 status",
    "Show me system statistics",
    "Show me recent invoices",
    "How does fraud detection work?",
    "What are the latest processed invoices?"
  ];

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async (messageText?: string) => {
    const text = messageText || input.trim();
    if (!text || isLoading) return;

    const userMessage: ChatMessage = {
      id: generateId(),
      type: 'user',
      content: text,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await InvoiceChainApi.chatWithAgent(text);
      
      const agentMessage: ChatMessage = {
        id: generateId(),
        type: 'agent',
        content: response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, agentMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: generateId(),
        type: 'agent',
        content: `Sorry, I encountered an error: ${handleApiError(error)}. Please try again or rephrase your question.`,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatMessageContent = (content: string) => {
    // Simple markdown-like formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/•/g, '•')
      .replace(/\n/g, '<br />');
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Page Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Chat with Your Invoice Agent
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Ask natural language questions about your invoices, validation status, 
          fraud analysis, and system statistics. All data remains privacy-protected.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Example Prompts Sidebar */}
        <div className="lg:col-span-1">
          <div className="card sticky top-4">
            <h3 className="flex items-center space-x-2 text-lg font-semibold text-gray-900 mb-4">
              <Lightbulb className="h-5 w-5 text-yellow-500" />
              <span>Try asking...</span>
            </h3>
            <div className="space-y-2">
              {examplePrompts.map((prompt, index) => (
                <button
                  key={index}
                  onClick={() => sendMessage(prompt)}
                  disabled={isLoading}
                  className="w-full text-left p-3 text-sm rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  "{prompt}"
                </button>
              ))}
            </div>
            
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start space-x-2">
                <CheckCircle className="h-5 w-5 text-blue-500 mt-0.5" />
                <div>
                  <h4 className="font-medium text-blue-900">Privacy Note</h4>
                  <p className="text-sm text-blue-700 mt-1">
                    Agent responses only include metadata and validation results. 
                    Sensitive invoice content is never exposed.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Chat Interface */}
        <div className="lg:col-span-3">
          <div className="card p-0 overflow-hidden">
            {/* Messages */}
            <div className="h-96 overflow-y-auto p-6 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    'flex space-x-3',
                    message.type === 'user' ? 'justify-end' : 'justify-start'
                  )}
                >
                  {message.type === 'agent' && (
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
                        <Bot className="h-4 w-4 text-white" />
                      </div>
                    </div>
                  )}
                  
                  <div
                    className={cn(
                      'max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-lg',
                      message.type === 'user'
                        ? 'bg-primary-500 text-white'
                        : 'bg-gray-100 text-gray-900'
                    )}
                  >
                    <div
                      dangerouslySetInnerHTML={{
                        __html: formatMessageContent(message.content)
                      }}
                      className="text-sm"
                    />
                    <div
                      className={cn(
                        'text-xs mt-2 opacity-75',
                        message.type === 'user' ? 'text-primary-100' : 'text-gray-500'
                      )}
                    >
                      <Clock className="h-3 w-3 inline mr-1" />
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>

                  {message.type === 'user' && (
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-gray-500 rounded-full flex items-center justify-center">
                        <User className="h-4 w-4 text-white" />
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {isLoading && (
                <div className="flex space-x-3 justify-start">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
                      <Bot className="h-4 w-4 text-white" />
                    </div>
                  </div>
                  <div className="bg-gray-100 px-4 py-3 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <Loader2 className="h-4 w-4 animate-spin text-gray-500" />
                      <span className="text-sm text-gray-600">Agent is thinking...</span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t bg-gray-50 p-4">
              <form onSubmit={handleSubmit} className="flex space-x-4">
                <div className="flex-1">
                  <input
                    ref={inputRef}
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask about invoice status, fraud analysis, system stats..."
                    disabled={isLoading}
                    className="input-field"
                  />
                </div>
                <button
                  type="submit"
                  disabled={!input.trim() || isLoading}
                  className="btn-primary"
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </button>
              </form>
              
              <div className="flex items-center justify-between mt-3 text-xs text-gray-500">
                <span>Press Enter to send, Shift+Enter for new line</span>
                <div className="flex items-center space-x-1">
                  <MessageCircle className="h-3 w-3" />
                  <span>Powered by uAgents ChatProtocol</span>
                </div>
              </div>
            </div>
          </div>

          {/* Chat Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            <div className="card">
              <div className="flex items-center space-x-3">
                <CheckCircle className="h-8 w-8 text-success-500" />
                <div>
                  <h4 className="font-medium text-gray-900">Invoice Status</h4>
                  <p className="text-sm text-gray-600">Check validation status and scores</p>
                </div>
              </div>
            </div>
            
            <div className="card">
              <div className="flex items-center space-x-3">
                <MessageCircle className="h-8 w-8 text-primary-500" />
                <div>
                  <h4 className="font-medium text-gray-900">Risk Analysis</h4>
                  <p className="text-sm text-gray-600">Get fraud risk assessments</p>
                </div>
              </div>
            </div>
            
            <div className="card">
              <div className="flex items-center space-x-3">
                <Bot className="h-8 w-8 text-indigo-500" />
                <div>
                  <h4 className="font-medium text-gray-900">System Stats</h4>
                  <p className="text-sm text-gray-600">View processing statistics</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
