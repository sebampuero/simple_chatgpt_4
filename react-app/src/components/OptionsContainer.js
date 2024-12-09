import React, { useState, useEffect  } from 'react';
import './OptionsContainer.css'

const OptionsContainer = ({ 
  optionsVisible, 
  toggleSidebar, 
  newChat, 
  handleImageUpload, //TODO: re add this later
  selectedModel, 
  selectModel, 
  sidebarVisible }) => {
    
  const [models, setModels] = useState({});

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = () => {
    const token = localStorage.getItem('jwt');
    fetch(`${process.env.PUBLIC_URL}/api/models`, {
      method: "GET",
      headers: {
        "Authorization": token
      }
    })
    .then((response) => { 
      if(response.status === 200) return response.json();
      throw new Error(response.status)
    })
    .then((resp) => {
      setModels(resp);
    }).catch((error) => {
      console.error("Error loading models:", error);
      alert("There was an error loading the models, please reload the page.")
    });
  }
  
  return (
    <div id="options-container" className={optionsVisible ? 'show' : 'hidden'}>
      <div>
        <button id="toggle-sidebar-button" className="custom-file-upload" onClick={toggleSidebar}>
          {sidebarVisible ? 'Hide chats' : 'Show chats'}
        </button>
      </div>
      <div>
        <button id="new-chat-button" className="custom-file-upload" onClick={newChat}>
          New chat
        </button>
      </div>
      <div>
      </div>

      {Object.entries(models).map(([category, llms]) => (
        <div key={category}>
          <p>{category}</p>
          <div className="llms">
            {llms.map((llm) => (
              <button
                id={`${llm.toLowerCase()}-button`}
                className={`custom-file-upload ${selectedModel === llm ? 'selected' : ''}`}
                onClick={() => selectModel(llm, category)}
              >
                {llm}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

  export default OptionsContainer;