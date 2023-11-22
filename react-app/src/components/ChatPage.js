import React, { useState, useEffect } from 'react';
import ChatSidebar from './ChatSidebar'; // Import your ChatSidebar component
import './ChatPage.css'; // Import your CSS file

const ChatPage = ({ code }) => {
  const [messageInput, setMessageInput] = useState('');
  const [optionsVisible, setOptionsVisible] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chats, setChats] = useState(
    Array.from({ length: 50 }, (_, index) => ({ id: index + 1, title: `Chat ${index + 1}` }))
  );
  const [currentChatId, setCurrentChatId] = useState(null);
  const [socket, setSocket] = useState(null);
  const [sidebarVisible, setSidebarVisible] = useState(true);

  useEffect(() => {
    // Set up WebSocket connection when the component mounts
    const socket = new WebSocket('ws://192.168.0.14:9292/ws'); // Replace with your WebSocket URL

    // Add event listeners for WebSocket
    socket.addEventListener('open', () => {
      console.log('WebSocket connection opened');
    });

    socket.addEventListener('message', (event) => {
      handleReceivedMessage(event.data);
    });

    socket.addEventListener('error', (event) => {
      console.error('WebSocket error:', event);
    });

    socket.addEventListener('close', (event) => {
      console.log('WebSocket connection closed:', event);
    });

    setSocket(socket);

    // Clean up WebSocket connection when the component unmounts
    return () => {
      if (socket) {
        socket.close();
      }
    };
  }, []);

  const displayMessage = (messageContent, messageType) => {
    const newMessage = {
      timestamp: Date.now(), 
      content: messageContent,
      type: messageType,
    };
    setChatMessages((prevMessages) => [...prevMessages, newMessage]);
  };

  const handleReceivedMessage = (message) => {
    const messageObj = JSON.parse(message)
    console.log(messageObj.content, messageObj.timestamp)
    setChatMessages((prevMessages) => {
      const existingMessageIndex = prevMessages.findIndex((msg) => msg.timestamp === messageObj.timestamp);
      console.log(existingMessageIndex);
      if (existingMessageIndex !== -1) {
        const updatedMessages = [...prevMessages];
        updatedMessages[existingMessageIndex].content += messageObj.content;
        return updatedMessages;
      } else {
        return [...prevMessages, { timestamp: messageObj.timestamp, content: messageObj.content, type: 'peer' }];
      }
    });
  };

  const handleImageUpload = (e) => {
    // Handle image upload logic here
  };

  const sendMessage = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      const message = {
        msg: messageInput,
        code: code,
        image: ''
      };
      socket.send(JSON.stringify(message));
      setMessageInput('');
    }
    displayMessage(messageInput, 'user');
  };

  const showOptions = () => {
    setOptionsVisible(!optionsVisible);
  }

  const switchChat = (chatId) => {
    setCurrentChatId(chatId);
  };

  const toggleSidebar = () => {
    setSidebarVisible(!sidebarVisible);
  };

  const deleteChat = (chatId) => {
    // Implement logic to delete the chat with the given ID
    setChats((prevChats) => prevChats.filter((chat) => chat.id !== chatId));
  };

  return (
    <div id="chat-container" style={{ display: 'flex' }}>
      {sidebarVisible && (
        <ChatSidebar chats={chats} onChatClick={switchChat} onDeleteChat={deleteChat} />
      )}
      <div id="content-container" style={{ flex: 1 }}>
        <div id="chat-messages">
        {chatMessages.map((message) => (
            <div key={message.timestamp} className={`message-bubble ${message.type === 'user' ? 'user-message' : 'peer-message'}`}>
              <span>{message.content}</span>
            </div>
          ))}
        </div>
      </div>
      <div id="chat-input">
        <textarea
          id="message-input"
          rows="1"
          style={{ resize: 'none' }}
          value={messageInput}
          onChange={(e) => setMessageInput(e.target.value)}
        ></textarea>
        <button id="send-button" onClick={sendMessage}>
          <i className="fa fa-arrow-right"></i>
        </button>
        <button id="reset-button" onClick={showOptions}>
          <i className="fas fa-bars"></i>
        </button>
      </div>

      <div id="options-container" className={optionsVisible ? 'show' : 'hidden'}>
        <div id="options-header">Options</div>
        <button id="toggle-sidebar-button" style={{marginTop: "5px", marginBottom: "5px"}} onClick={toggleSidebar}>
          {sidebarVisible ? 'Hide chats' : 'Show chats'}
        </button>
        <div id="image-upload-container">
          <input
            type="file"
            id="image-input"
            accept="image/*"
            onChange={(e) => handleImageUpload(e)}
          />
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
