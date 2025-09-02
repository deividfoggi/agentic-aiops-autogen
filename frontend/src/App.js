import React, { useState, useEffect, useRef } from 'react';
import ChatWindow from './components/ChatWindow';
import MessageInput from './components/MessageInput';
import './styles/chat.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [connecting, setConnecting] = useState(true);
  const wsRef = useRef(null);
  const chatEndRef = useRef(null); // Ref to track the end of the chat window

  // Connect to WebSocket when component mounts
  useEffect(() => {
    connectWebSocket();
    
    // Cleanup function
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Scroll to the bottom whenever messages change
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const connectWebSocket = () => {
    setConnecting(true);
    
    const ws = new WebSocket('ws://20.66.11.121/ws');
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
      setConnecting(false);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('WebSocket message received:', data);
      
      const sender = data.sender || 'Problema que será resolvido'; // Default sender name
      if (data.text) {
        setMessages(prev => [...prev, { 
          sender: sender, 
          text: data.text 
        }]);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setConnecting(true);
      setTimeout(connectWebSocket, 2000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      ws.close();
    };
  };

  const sendMessage = (text) => {
    if (!text.trim()) return;

    // If it's the first message, prepend the agent's title to the user message
    if (messages.length === 0) {
      setMessages(prev => [...prev, { 
        sender: 'Problema que será resolvido', 
        text: text // Use the input text for the first message
      }]);
    } else {
      // Show user input as a console command with $ prompt
      const userMessage = { sender: 'user', text: `$ ${text}` };
      setMessages(prev => [...prev, userMessage]);
    }

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ event: text }));
    } else {
      sendMessageHttp(text);
    }
  };

  const sendMessageHttp = async (text) => {
    try {
      const response = await fetch('http://20.66.11.121/run_task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event: text }),
      });

      const data = await response.json();
      const agentMessage = { sender: 'agent', text: data.response };
      setMessages(prev => [...prev, agentMessage]);
    } catch (error) {
      console.error('Error sending message via HTTP:', error);
      setMessages(prev => [...prev, { 
        sender: 'system', 
        text: 'Failed to send message. Please try again.' 
      }]);
    }
  };

  return (
    <div className="app-container">
      {connecting && (
        <div className="connecting-overlay">
          <p>Connecting to server...</p>
        </div>
      )}
      <ChatWindow messages={messages} chatEndRef={chatEndRef} />
      <MessageInput onSend={sendMessage} />
    </div>
  );
}

export default App;
