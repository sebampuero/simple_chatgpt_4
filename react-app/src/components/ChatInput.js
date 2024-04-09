import React from 'react';

const ChatInput = ({ sendMessage, messageInput, setMessageInput, isPromptLoading, showOptions, setOptionsVisible, setSidebarVisible }) => {
    return (
      <div id="chat-input">
        <textarea
          id="message-input"
          rows="1"
          style={{ resize: 'none' }}
          value={messageInput}
          onChange={(e) => setMessageInput(e.target.value)}
          onFocus={() => {
            setSidebarVisible(false);
            setOptionsVisible(false);
          }}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              sendMessage(); 
            }
          }}
        ></textarea>
        <button id="send-button" onClick={sendMessage} disabled={isPromptLoading}>
          {isPromptLoading ? (
            <i className="fa fa-spinner fa-spin"></i>
          ) : (
            <i className="fa fa-arrow-right"></i>
          )}
        </button>
        <button id="reset-button" onClick={showOptions}>
          <i className="fas fa-bars"></i>
        </button>
      </div>
    );
  };

  export default ChatInput;