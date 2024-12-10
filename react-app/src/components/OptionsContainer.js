import React, { useState, useEffect  } from 'react';
import './OptionsContainer.css'

const OptionsContainer = ({ 
  optionsVisible, 
  toggleSidebar, 
  newChat, 
  handleImageUpload, //TODO: re add this later
  selectedModel, 
  selectedCategory,
  selectModel, 
  selectCategory,
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

  const handleModelSelect = (model) => {
    selectModel(model);
  };
  
  return (
    optionsVisible && (
      <div id="options-dialog" className="dialog">
        <div className="dialog-content">
          <button id="toggle-sidebar-button" className="dialog-button" onClick={toggleSidebar}>
            {sidebarVisible ? 'Hide chats' : 'Show chats'}
          </button>
          <button id="new-chat-button" className="dialog-button" onClick={newChat}>
            New chat
          </button>
          <div className="dialog-categories">
            {Object.keys(models).map((category) => (
              <button
                key={category}
                className={`dialog-button ${selectedCategory === category ? 'selected' : ''}`}
                onClick={() => selectCategory(category, models[category][0])}
              >
                {category}
              </button>
            ))}
          </div>
          {selectedCategory && (
            <div className="dialog-models">
              {models[selectedCategory].map((model) => (
                <button
                  key={model}
                  className={`dialog-button ${selectedModel === model ? 'selected' : ''}`}
                  onClick={() => handleModelSelect(model)}
                >
                  {model}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    )
  );
};

  export default OptionsContainer;