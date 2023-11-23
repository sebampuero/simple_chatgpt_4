import React, { useState, useEffect } from 'react';
import ChatSidebar from './ChatSidebar';
import './ChatPage.css';

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
  const [isPromptLoading, setIsPromptLoading] = useState(false);
  const [imgBase64Data, setImageBase64Data] = useState('');
  const [imageDataURL, setImageDataURL] = useState(null);
  const MAX_IMG_WIDTH = 450;
  const MAX_IMG_HEIGHT = 450;

  useEffect(() => {
    const socketUrl = process.env.NODE_ENV === 'production'
      ? process.env.REACT_APP_PROD_WS_URL
      : process.env.REACT_APP_WS_URL;
    const socket = new WebSocket(socketUrl);

    socket.addEventListener('open', () => {
      console.log('WebSocket connection opened');
    });

    socket.addEventListener('message', (event) => {
      handleReceivedMessage(event.data);
    });

    socket.addEventListener('error', (event) => {
      console.error('WebSocket error:', event);
      alert("There was an error, try again later.");
    });

    socket.addEventListener('close', (event) => {
      console.log('WebSocket connection closed:', event);
      alert("Connection closed");
    });

    setSocket(socket);

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
      img: imageDataURL
    };
    setChatMessages((prevMessages) => [...prevMessages, newMessage]);
  };

  const handleReceivedMessage = (message) => {
    const messageObj = JSON.parse(message)
    if (messageObj.content === "END") {
      setIsPromptLoading(false);
      setImageBase64Data('');
      setImageDataURL(null);
      return
    }
    setChatMessages((prevMessages) => {
      const existingMessageIndex = prevMessages.findIndex((msg) => msg.timestamp === messageObj.timestamp);
      if (existingMessageIndex !== -1) {
        const updatedMessages = [...prevMessages];
        updatedMessages[existingMessageIndex].content += messageObj.content;
        return updatedMessages;
      } else {
        const newMessage = {
          timestamp: messageObj.timestamp,
          content: messageObj.content,
          type: 'peer',
        };
        return [...prevMessages, newMessage];
      }
    });
  };

  const resizeImageAndConvertToBase64 = (binaryData, maxWidth, maxHeight) => {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.src = URL.createObjectURL(new Blob([new Uint8Array(binaryData)]));
      img.onload = function () {
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");

        let width = img.width;
        let height = img.height;

        if (width > maxWidth) {
          height *= maxWidth / width;
          width = maxWidth;
        }

        if (height > maxHeight) {
          width *= maxHeight / height;
          height = maxHeight;
        }

        canvas.width = width;
        canvas.height = height;

        ctx.drawImage(img, 0, 0, width, height);

        canvas.toBlob(blob => {
          setImageDataURL(URL.createObjectURL(blob));
          const reader = new FileReader();
          reader.onload = function () {
            resolve(reader.result.split(',')[1]);
          };

          reader.readAsDataURL(blob);
        }, 'image/jpeg');
      };

      img.onerror = reject;
    });
  }
  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        resizeImageAndConvertToBase64(e.target.result, MAX_IMG_WIDTH, MAX_IMG_HEIGHT)
        .then(base64Data => {
          setImageBase64Data(base64Data);
        })
        .catch(error => {
          console.error('Error:', error);
          alert("There was an error uploading the image");
          setImageBase64Data('');
          setImageDataURL(null);
        });
      };
      reader.readAsArrayBuffer(file);
    }
  };

  const sendMessage = () => {
    if (messageInput.trim() === '') return
    if (socket && socket.readyState === WebSocket.OPEN) {
      const message = {
        msg: messageInput,
        code: code,
        image: imgBase64Data
      };
      socket.send(JSON.stringify(message));
      setMessageInput('');
    }
    displayMessage(messageInput, 'user');
    setIsPromptLoading(true);
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
    // TODO: implement delete chat functionality, this should send a DELETE request for the given chat
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
              {message.img && message.img !== null && (
                <img src={message.img} alt="GPT4-V image prompt" />
              )}
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
        <button id="send-button" onClick={sendMessage} disabled={isPromptLoading}>
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
