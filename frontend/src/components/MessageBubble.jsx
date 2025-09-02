// src/components/MessageBubble.jsx

const MessageBubble = ({ sender, message, index }) => {
  // Extract text and timestamp from message (could be string or object)
  const messageText = typeof message === 'string' ? message : message.text || message;
  const messageTimestamp = typeof message === 'object' ? message.timestamp : null;
  
  // Add timestamp - use message timestamp if available, otherwise current time
  const timestamp = messageTimestamp || new Date().toLocaleTimeString();
  
  // Console-style class for all messages
  const getSenderClass = (sender) => {
    const senderLower = sender.toLowerCase();
    return `message-bubble console ${senderLower}`;
  };

  const getSenderName = (sender) => {
    // Map sender types to display names
    const senderMap = {
      'user': 'USER',
      'system': 'SYSTEM',
      'command': 'CMD',
      'error': 'ERROR',
      'stdout': 'OUT',
      'stderr': 'ERR',
      'log_info': 'INFO',
      'log_warning': 'WARN',
      'log_error': 'ERROR',
      'log_debug': 'DEBUG',
      'MagenticOneOrchestrator': 'ORCHESTRATOR'
    };
    
    return senderMap[sender] || sender.toUpperCase();
  };

  return (
    <div className="message-container console-style">
      <div className={getSenderClass(sender)}>
        <span className="console-timestamp">[{timestamp}]</span>
        <span className="console-sender">{getSenderName(sender)}:</span>
        <span className="console-message">{messageText}</span>
      </div>
    </div>
  );
};

const MessageList = ({ messages }) => {
  return (
    <div className="message-list">
      {messages.map((msg, idx) => (
        <MessageBubble 
          key={idx} 
          sender={msg.sender} 
          message={msg.text} 
          index={idx} // Pass the index here
        />
      ))}
    </div>
  );
};

export default MessageBubble;
export { MessageList };