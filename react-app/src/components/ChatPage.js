import React, { useState, useEffect, useRef  } from 'react';
import './ChatPage.css';
import ChatSidebar from './ChatSidebar';
import ChatInput from './ChatInput';
import ChatMessages from './ChatMessages';
import OptionsContainer from './OptionsContainer';
import { fetchWithToken } from '../api/api';

const ChatPage = ({ email }) => {
  const [messageInput, setMessageInput] = useState('');
  const [optionsVisible, setOptionsVisible] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chats, setChats] = useState([]);
  const [socket, setSocket] = useState(null);
  const [sidebarVisible, setSidebarVisible] = useState(false);
  const [isPromptLoading, setIsPromptLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState("mistral-small-latest");
  const [selectedCategory, setSelectedCategory] = useState("Mistral");
  const [allChatsLoaded, setAllChatsLoaded] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const currentSocketId = useRef("");
  const currentChatId = useRef("");
  const currentChatTimestamp = useRef(0);
  const imageDataURL = useRef(null);
  const imgBase64Data = useRef("");
  const selectedModelRef = useRef(selectedModel);
  const categoryRef = useRef(selectedCategory);
  const lastEvalKey = useRef("");
  const isInitialMount = useRef(true);

  const PAGINATION_LIMIT = 10;
  const MAX_IMG_WIDTH = 650;
  const MAX_IMG_HEIGHT = 650;

  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }

    const handler = setTimeout(() => {
      searchChats(searchTerm);
    }, 500);

    return () => {
      clearTimeout(handler);
    };
  }, [searchTerm]);

  useEffect(() => {
    const model = localStorage.getItem('model')
    const category = localStorage.getItem('category')
    if (model && category) {
      setSelectedModel(model)
      setSelectedCategory(category)
    }
    if (!socket){
      createSocket()
    }
  }, [socket]); // needed here because rendering is needed every time a new chat is selected

  useEffect(() => {
    selectedModelRef.current = selectedModel;
    categoryRef.current = selectedCategory;
  }, [selectedModel, selectedCategory]);

  const searchChats = (query) => {
    if (query) {
      loadChatsByKeywords(query)
    }else{
      loadChats();
      setAllChatsLoaded(false);
    }
  };

  const loadChatsByKeywords = (keywords) => {
    const token = localStorage.getItem('jwt');
    fetchWithToken(`${process.env.PUBLIC_URL}/api/search_for_chat` , {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": token
      },
      body: JSON.stringify({"keywords": keywords, "email_address": email})
    })
      .then((response) => { 
        if(response.status === 200) return response.json();
        throw new Error(response.status)
      })
      .then((resp) => {
        const responseChats = resp.chats
        console.log(responseChats)
        responseChats.forEach(obj => {
          let userContent = obj.messages.find(msg => msg.role === 'user')?.content;
          obj.title = userContent.substring(0,25) + "...";
        })
        setChats(responseChats);
        setAllChatsLoaded(true);
      })
      .catch(handleChatsLoadedError);
  }

  const loadChats = () => {
    const token = localStorage.getItem('jwt');
    fetchWithToken(`${process.env.PUBLIC_URL}/api/user?email=${email}&limit=${PAGINATION_LIMIT}` , {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": token
      }
    })
      .then((response) => { 
        if(response.status === 200) return response.json();
        throw new Error(response.status)
      })
      .then((resp) => {
        const responseChats = resp.chats
        lastEvalKey.current = JSON.stringify(resp.lastEvalKey)
        responseChats.forEach(obj => {
          let userContent = obj.messages.find(msg => msg.role === 'user')?.content;
          obj.title = userContent.substring(0,25) + "..."; // very basic and naive way to show main idea of a chat
        })
        setChats(responseChats);
      })
      .catch(handleChatsLoadedError);
  }

  const loadMoreChats = () => {
    const token = localStorage.getItem('jwt');
    fetchWithToken(`${process.env.PUBLIC_URL}/api/user?email=${email}&last_eval_key=${lastEvalKey.current}&limit=${PAGINATION_LIMIT}` , {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": token
      }
    })
      .then((response) => { 
        if(response.status === 200) return response.json();
        throw new Error(response.status)
      })
      .then((resp) => {
        const responseChats = resp.chats
        lastEvalKey.current = JSON.stringify(resp.lastEvalKey)
        if(lastEvalKey.current === "null"){
          setAllChatsLoaded(true);
        }
        const updatedChats = [...chats];
        responseChats.forEach(obj => {
          let userContent = obj.messages.find(msg => msg.role === 'user')?.content;
          obj.title = userContent.substring(0,25) + "..."; // very basic and naive way to show main idea of a chat
          updatedChats.push(obj);
        })
        setChats(updatedChats);
      })
      .catch(handleChatsLoadedError);
  }

  const handleChatsLoadedError = (error) => {
    console.error("Error:", error);
    if (error.message === "401") {
        alert("Please reload the page and log in again");
    } else if (error.message === "400") {
        alert("There was a problem loading your chats!");
    } else {
        alert("There was an error, please try again later");
    }
  }

  const createSocket = () => {
    if(!socket){
      const socketUrl = process.env.NODE_ENV === 'production'
      ? process.env.REACT_APP_PROD_WS_URL
      : process.env.REACT_APP_WS_URL;
      const socket = new WebSocket(socketUrl);

      socket.addEventListener('message', (event) => {
        processMessageType(event.data)
      });

      socket.addEventListener('error', (event) => {
        console.error('WebSocket error:', event);
        alert("There was an error, try again later.");
      });

      setSocket(socket);
      loadChats();
    }
  }

  const closeSocket = () => {
    if (socket) {
      socket.close()
      setSocket(null)
    }
  }

  const displayMessage = (messageContent, messageType) => {
    const newMessage = {
      timestamp: Date.now(), 
      content: messageContent,
      role: messageType,
      image: imageDataURL.current
    };
    setChatMessages((prevMessages) => [...prevMessages, newMessage]);
  };
  const retrieveMessagesForNewOpenedChat = (newSocketId) => {
    const token = localStorage.getItem('jwt');
    fetchWithToken(`${process.env.PUBLIC_URL}/api/chat/${currentChatId.current}/${currentChatTimestamp.current}/${newSocketId}/${currentSocketId.current}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": token
      }
    })
      .then((response) => { 
        if (response.status === 200) return response.json();
        else throw new Error(response.status)
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
        if (error.message === "401") alert("Please reload the page and log back in")
        else if (error.message === "404") alert("Could not find Chat")
        else alert("There was an error, please try again later")
      });
  }
  const processMessageType = (data) => {
    const msg = JSON.parse(data);
    if (msg.type === "INIT"){
      sendNewModel(selectedModelRef.current, categoryRef.current, msg.socket_id)
      if(currentChatId.current != "") { // socket id is generated by the backend
        retrieveMessagesForNewOpenedChat(msg.socket_id)
      }
      currentSocketId.current = msg.socket_id
    }else if(msg.type === "CONTENT"){
      handleReceivedMessage(data)
    }else if(msg.type == "ERROR"){
      alert("There was an error, please reload the page.")
    }
  }

  const handleReceivedMessage = (message) => {
    const messageObj = JSON.parse(message)
    if (messageObj.content === "END") {
      setIsPromptLoading(false);
      imgBase64Data.current = "";
      imageDataURL.current = null;
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
          language_model: selectedModelRef.current
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
          imageDataURL.current = URL.createObjectURL(blob);
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
          alert("Image loaded!")
          imgBase64Data.current = base64Data;
        })
        .catch(error => {
          console.error('Error:', error);
          alert("There was an error uploading the image");
          imgBase64Data.current = "";
          imageDataURL.current = null;
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
        chat_id: currentChatId.current,
        image: imgBase64Data.current
      };
      socket.send(JSON.stringify(message));
      setMessageInput('');
    }else{
      alert("The connection to the server is closed, please reload the page.")
    }
    displayMessage(messageInput, 'user');
    setIsPromptLoading(true);
  };

  const showOptions = () => {
    setOptionsVisible(!optionsVisible);
  }

  const switchChat = (chatId, timestamp) => {
    console.log("Switching chat to " + chatId)
    currentChatId.current = chatId;
    currentChatTimestamp.current = timestamp;
    closeSocket();
    createSocket();
    setSidebarVisible(false);
    setOptionsVisible(false);
  };

  const newChat = () => {
    setChatMessages([]);
    currentChatId.current = "";
    imgBase64Data.current = "";
    imageDataURL.current = null;
    closeSocket();
    createSocket();
    setSidebarVisible(false);
    setOptionsVisible(false);
  }

  const toggleSidebar = () => {
    setSidebarVisible(!sidebarVisible);
  };

  const deleteChat = (chatId, timestamp) => {
    const token = localStorage.getItem('jwt');
    fetchWithToken(`${process.env.PUBLIC_URL}/api/chat/${chatId}/${timestamp}`, {
      method: "DELETE",
      headers: {
        "Authorization": token
      }
    })
      .then((response) => { 
        if(response.status === 204) setChats((prevChats) => prevChats.filter((chat) => chat.chat_id !== chatId));
        else throw new Error("Could not delete chat with ID " + chatId)
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("There was a problem deleting the chat.")
      });
  };

  const sendNewModel = (model, category, socket_id) => {
    const token = localStorage.getItem('jwt');
    fetchWithToken(`${process.env.PUBLIC_URL}/api/model/${socket_id}`, {
      method: "POST",
      headers: {
        "Authorization": token
      },
      body: JSON.stringify({"model": model, "category": category})
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("There was a problem setting the model, please try again.")
    });
  }

  const selectCategory = (category, defaultModel) => {
    setSelectedCategory(category)
    setSelectedModel(defaultModel)
    categoryRef.current = category
    selectedModelRef.current = defaultModel
    localStorage.setItem('category', category);
    localStorage.setItem('model', defaultModel)
  }

  const selectModel = (model) => {
    setSelectedModel(model);
    selectedModelRef.current = model
    localStorage.setItem('model', model);
    sendNewModel(model, categoryRef.current, currentSocketId.current);
  };

  const handleLoadMore = () => {
    loadMoreChats();
  }

  const handleSearchChat = (event) => {
    setSearchTerm(event.target.value);
  }
  
    return (
      <div id="chat-container" style={{ display: 'flex' }}>
        {sidebarVisible && <ChatSidebar 
            chats={chats} 
            onChatClick={switchChat} 
            onDeleteChat={deleteChat} 
            onLoadMoreClick={handleLoadMore}
            allChatsLoaded={allChatsLoaded}
            onSearchChat={handleSearchChat}/>}
        <div id="content-container" style={{ flex: 1 }}>
          <ChatMessages messages={chatMessages} />
        </div>
        <ChatInput
          sendMessage={sendMessage}
          messageInput={messageInput}
          setMessageInput={setMessageInput}
          isPromptLoading={isPromptLoading}
          handleImageUpload={handleImageUpload}
          showOptions={showOptions}
          setOptionsVisible={setOptionsVisible}
          setSidebarVisible={setSidebarVisible}
        />
        <OptionsContainer
          optionsVisible={optionsVisible}
          toggleSidebar={toggleSidebar}
          newChat={newChat}
          handleImageUpload={handleImageUpload}
          selectedModel={selectedModel}
          selectedCategory={selectedCategory}
          selectModel={selectModel}
          selectCategory={selectCategory}
          sidebarVisible={sidebarVisible}
        />
      </div>
    );
  };

  export default ChatPage;