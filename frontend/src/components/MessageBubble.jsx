// src/components/MessageBubble.jsx

const MessageBubble = ({ sender, message, index }) => {
  // Map agent names to UI-friendly display
  const getSenderClass = (sender) => {
    return sender === 'MagenticOneOrchestrator' ? 'message-bubble MagenticOneOrchestrator' : 'message-bubble agent';
  };

  const getSenderName = (sender) => {
    return sender === 'MagenticOneOrchestrator' ? 'Magentic One Orchestrator' : sender;
  };

  // Determine alignment class for the message container
  const alignmentClass = (sender) => {
    return sender === 'MagenticOneOrchestrator' ? 'left' : 'right';
  };

  return (
    <div className={`message-container ${alignmentClass(sender)}`}>
      {sender !== 'user' && (
        <div className={`agent-name ${alignmentClass(sender)}`}>
          {getSenderName(sender)}
        </div>
      )}
      <div className={getSenderClass(sender)}>
        <span>{message}</span>
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