import React, { useState, useEffect } from 'react';
import ChatSidebar from './ChatSidebar';
import './ChatPage.css';

const ChatPage = ({ email }) => { //TODO: this component could be separated in more other components (messageinput, options dialog, etc)
  const [messageInput, setMessageInput] = useState('');
  const [optionsVisible, setOptionsVisible] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chats, setChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState("");
  const [currentChatTimestamp, setCurrentChatTimestamp] = useState(0);
  const [socket, setSocket] = useState(null);
  const [sidebarVisible, setSidebarVisible] = useState(false);
  const [isPromptLoading, setIsPromptLoading] = useState(false);
  const [imgBase64Data, setImageBase64Data] = useState('');
  const [imageDataURL, setImageDataURL] = useState(null);

  const MAX_IMG_WIDTH = 450;
  const MAX_IMG_HEIGHT = 450;

  const loadChats = () => {
    fetch(process.env.PUBLIC_URL + "/user/" + email, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      }
    })
      .then((response) => { 
        if(response.status === 400){
          throw new Error("Bad request sent")
        }
        if(response.status === 200){
          return response.json();
        }
      })
      .then((resp) => {
        const chats = resp.body
        chats.forEach(obj => {
          let userContent = obj.messages.find(msg => msg.role === 'user')?.content;
          obj.title = userContent.substring(0,10) + "..."; // very basic and naive way to show main idea of a chat
        })
        setChats(chats)
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("There was a problem loading your chats history!")
      });
  }

  const createSocket = () => {
    if(!socket){
      const socketUrl = process.env.NODE_ENV === 'production'
      ? process.env.REACT_APP_PROD_WS_URL
      : process.env.REACT_APP_WS_URL;
      const socket = new WebSocket(socketUrl);

      socket.addEventListener('open', () => {
        console.log('WebSocket connection opened');      
      });

      socket.addEventListener('message', (event) => {
        processMessageType(event.data)
      });

      socket.addEventListener('error', (event) => {
        console.error('WebSocket error:', event);
        alert("There was an error, try again later.");
      });

      socket.addEventListener('close', (event) => {
        console.log('WebSocket connection closed:', event);
      });

      setSocket(socket);
    }
  }

  const closeSocket = () => {
    if (socket) {
      socket.close()
      setSocket(null)
    }
  }

  useEffect(() => {
    loadChats()
    createSocket()
  }, [currentChatId, socket, currentChatTimestamp]); // needed here because rendering is needed every time a new chat is selected

  const displayMessage = (messageContent, messageType) => {
    const newMessage = {
      timestamp: Date.now(), 
      content: messageContent,
      role: messageType,
      img: imageDataURL
    };
    setChatMessages((prevMessages) => [...prevMessages, newMessage]);
  };
  const retrieveMessagesForNewOpenedChat = (socketId) => {
    fetch(process.env.PUBLIC_URL + `/chat/${currentChatId}/${currentChatTimestamp}/${socketId}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      }
    })
      .then((response) => { 
        if (response.status === 400){
          throw new Error("Bad request")
        }
        if (response.status === 404){
          throw new Error("Chat not found " + currentChatId)
        }
        return response.json();
      })
      .then((resp) => {
        const chat = resp.body
        setChatMessages(() => {
          chat.messages.forEach(obj => {
            if(obj.image) obj.image = `data:image/jpg;base64,${obj.image}`
          })
          return chat.messages
        })
      })
      .catch((error) => {
        console.error("Error: ", error);
        alert("There was a problem loading the chat, please refresh the page!")
      });
  }
  const processMessageType = (data) => {
    const msg = JSON.parse(data);
    if (msg.type === "INIT"){
      if(currentChatId != "") retrieveMessagesForNewOpenedChat(msg.socket_id)
    }else if(msg.type === "CONTENT"){
      handleReceivedMessage(data)
    }
  }

  const handleReceivedMessage = (message) => {
    const messageObj = JSON.parse(message)
    if (messageObj.content === "END") {
      setIsPromptLoading(false);
      setImageBase64Data('');
      setImageDataURL(null);
      //TODO: add option to format message when gpt sends code surrounded by `code`
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
          role: 'peer',
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
        email: email,
        chat_id: currentChatId,
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

  const switchChat = (chatId, timestamp) => {
    console.log("Switching chat to " + chatId)
    setCurrentChatId(chatId);
    setCurrentChatTimestamp(timestamp);
    closeSocket();
    createSocket();
  };

  const toggleSidebar = () => {
    setSidebarVisible(!sidebarVisible);
  };

  const deleteChat = (chatId, timestamp) => {
    fetch(process.env.PUBLIC_URL + `/chat/${chatId}/${timestamp}`, {
      method: "DELETE"
    })
      .then((response) => { 
        if(response.status === 204){
          setChats((prevChats) => prevChats.filter((chat) => chat.chat_id !== chatId));
        }else{
          throw new Error("Could not delete chat with ID " + chatId)
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("There was a problem deleting the chat.")
      });
  };

  return (
    <div id="chat-container" style={{ display: 'flex' }}>
      {sidebarVisible && (
        <ChatSidebar chats={chats} onChatClick={switchChat} onDeleteChat={deleteChat} />
      )}
      <div id="content-container" style={{ flex: 1 }}>
        <div id="chat-messages">
        {chatMessages.map((message) => (
            <div className={`message-bubble ${message.role === 'user' ? 'user-message' : 'peer-message'}`}>
              {message.image && message.image !== null && (
                <img src={message.image} alt="GPT4-V image prompt" />
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