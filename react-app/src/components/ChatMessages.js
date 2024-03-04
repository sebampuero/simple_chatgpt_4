import React from 'react';

const ChatMessages = ({ messages }) => {
    return (
      <div id="chat-messages">
        {messages.map((message) => (
           <div key={message.timestamp} className={`message-bubble ${message.role === 'user' ? 'user-message' : 'peer-message'}`}>
           {message.image && message.image !== null && (
             <img src={message.image} alt="GPT4-V image prompt" />
           )}
           <span>
            {message.content}
            {message.role !== 'user' && (
              <>
                <br></br>
                <br></br>
                <span style={{ fontWeight: 'bold', fontSize: '0.8em' }}>
                  {message.language_model}
                </span>
              </>
            )}
          </span>
         </div>
        ))}
      </div>
    );
  };

  export default ChatMessages;