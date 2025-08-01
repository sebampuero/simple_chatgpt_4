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

  const sessionId = useRef("");
  const chatId = useRef("");
  const imageDataURL = useRef(null);
  const imgBase64Data = useRef("");
  const selectedModelRef = useRef(selectedModel);
  const categoryRef = useRef(selectedCategory);
  const lastEvalKey = useRef("");
  const isInitialMount = useRef(true);

  const PAGINATION_LIMIT = 10;
  const MAX_IMG_WIDTH = 650;
  const MAX_IMG_HEIGHT = 650;
  const RETRY_DELAY_SECONDS = 2;

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
    try {
      sessionId.current = crypto.randomUUID();
    } catch(error){
      console.log("Failed to retrieve randomUUID, using fallback.");
      sessionId.current = "id" + Math.random().toString(16).slice(2)
    }
    loadNewChatState();
    sendNewModel(selectedModelRef.current, categoryRef.current, sessionId.current)
    return () => {
      if (socket) {
        socket.close();
      }
    }
  }, []); // loading on first render

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
    fetchWithToken(`${process.env.PUBLIC_URL}/api/search_for_chat` , {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
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
    fetchWithToken(`${process.env.PUBLIC_URL}/api/user?email=${email}&limit=${PAGINATION_LIMIT}` , {
      method: "GET",
      headers: {
        "Content-Type": "application/json"
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
          if (userContent != undefined) {
            obj.title = userContent.substring(0,35) + "..."; // very basic and naive way to show main idea of a chat
          }
        })
        setChats(responseChats);
      })
      .catch(handleChatsLoadedError);
  }

  const loadMoreChats = () => {
    fetchWithToken(`${process.env.PUBLIC_URL}/api/user?email=${email}&last_eval_key=${lastEvalKey.current}&limit=${PAGINATION_LIMIT}` , {
      method: "GET",
      headers: {
        "Content-Type": "application/json"
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
      window.location.reload();
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
        alert("There was an error with the connection, try again later.");
      });

      socket.addEventListener('open', () => {
        console.log('Socket connected');
      });
      
      socket.addEventListener('close', (event) => {
        console.log("Disconnected, trying to reconnect...")
        setTimeout(() => {
          createSocket();
        }, RETRY_DELAY_SECONDS * 1000);
      });

      setSocket(socket);
      loadChats();
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

  const loadNewChatState = () => {
    fetchWithToken(`${process.env.PUBLIC_URL}/api/chat_state/${sessionId.current}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({"email": email})
    })
    .then((response) => { 
      if (response.status !== 200) throw new Error(response.status);
    })
    .catch((error) => {
      console.error("Chat state could not be cleared: ", error);
      alert("There was an error opening a new chat, please reload the page or try again later.")
    });
  }

  const retrieveMessagesForNewOpenedChat = () => {
    fetchWithToken(`${process.env.PUBLIC_URL}/api/chat/${chatId.current}/${sessionId.current}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json"
      }
    })
      .then((response) => { 
        if (response.status === 200) return response.json();
        if (response.status === 206) {
          alert("The websocket connection is closed, the chat functionaliy wont work, please reload the page")
          return response.json();
        }
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
        if (error.message === "401") window.location.reload()
        else if (error.message === "404") alert("Could not find Chat")
        else alert("There was an error, please try again later")
      });
  }
  const processMessageType = (data) => {
    const msg = JSON.parse(data);
    if(msg.type === "CONTENT"){
      handleReceivedMessage(data)
    }else if(msg.type === "ERROR"){
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
        chat_id: chatId.current,
        image: imgBase64Data.current,
        session_id: sessionId.current
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

  const switchChat = (newChatId) => {
    console.log("Switching chat to " + newChatId)
    chatId.current = newChatId;
    retrieveMessagesForNewOpenedChat()
    loadChats();
    setSidebarVisible(false);
    setOptionsVisible(false);
  };

  const newChat = () => {
    setChatMessages([]);
    chatId.current = "";
    imgBase64Data.current = "";
    imageDataURL.current = null;
    setSidebarVisible(false);
    setOptionsVisible(false);
    loadNewChatState();
    loadChats();
  }

  const toggleSidebar = () => {
    setSidebarVisible(!sidebarVisible);
  };

  const deleteChat = (toDeleteChatId, timestamp) => {
    fetchWithToken(`${process.env.PUBLIC_URL}/api/chat/${toDeleteChatId}/${timestamp}`, {
      method: "DELETE"
    })
    .then((response) => { 
      if(response.status === 204) setChats((prevChats) => prevChats.filter((chat) => chat.chat_id !== toDeleteChatId));
      else throw new Error(response.status)
    })
    .catch((error) => {
      console.error("Error:", error);
      if (error.message === '401') window.location.reload()
      else alert("There was a problem deleting the chat.")
    });
    if (toDeleteChatId === chatId.current) {
      newChat();
    }
  };

  const sendNewModel = (model, category, socket_id) => {
    fetchWithToken(`${process.env.PUBLIC_URL}/api/model/${socket_id}`, {
      method: "POST",
      body: JSON.stringify({"model": model, "category": category})
    })
    .then((response) => {
      if (response.status > 399) throw new Error(response.status)
    })
    .catch((error) => {
      console.error("Error:", error);
      if (error.message === '401') window.location.reload();
      else alert("There was an error setting the model, please try again later.")
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
    sendNewModel(model, categoryRef.current, sessionId.current);
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