// src/components/MessageInput.jsx
import React, { useState } from 'react';

const MessageInput = ({ onSend }) => {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim()) {
      onSend(message);
      setMessage('');
    }
  };

  return (
    <div className="message-input">
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="$ Enter command or describe the problem..."
        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
      />
      <button onClick={handleSend}>Execute</button>
    </div>
  );
};

export default MessageInput;