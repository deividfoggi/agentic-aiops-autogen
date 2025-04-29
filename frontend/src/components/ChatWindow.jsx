// src/components/ChatWindow.jsx
import React, { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';

const ChatWindow = ({ messages }) => {
  const chatEndRef = useRef(null);

  // Scroll to the bottom whenever messages change
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  return (
    <div className="chat-window">
      {messages.map((msg, index) => (
        <div key={index} className={`message-container ${msg.sender === 'user' ? 'right' : 'left'}`}>
          <MessageBubble sender={msg.sender} message={msg.text} />
        </div>
      ))}
      <div ref={chatEndRef} /> {/* This ensures the last bubble is always visible */}
    </div>
  );
};

export default ChatWindow;