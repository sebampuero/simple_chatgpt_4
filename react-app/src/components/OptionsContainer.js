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
    
  const [categoriesWithModels, setCategoriesWithModels] = useState({});
  const [canHandleImage, setCanHandleImage] = useState(false);

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
      setCategoriesWithModels(resp);
      console.log("Loaded categoriesWithModels: ", resp);
    }).catch((error) => {
      console.error("Error loading categoriesWithModels:", error);
      alert("There was an error loading the categoriesWithModels, please reload the page.")
    });
  }

  const handleModelSelect = (category, model) => {
    selectModel(model);
    const selectedModel = categoriesWithModels[category].models.find(m => m.name === model);
    setCanHandleImage(selectedModel.handles_image);
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
          canHandleImage && (
            <div id="image-upload-container">
              <input
                type="file"
                id="image-input"
                accept="image/*"
                onChange={(e) => handleImageUpload(e)}
              />
              <label htmlFor="image-input" className="custom-file-upload">
                Upload Image
              </label>
            </div>
          )
          <div className="dialog-categories">
            {Object.keys(categoriesWithModels).map((category) => (
              <button
                key={category}
                className={`dialog-button ${selectedCategory === category ? 'selected' : ''}`}
                onClick={() => selectCategory(category, categoriesWithModels[category].models[0].name)}
              >
                {category}
              </button>
            ))}
          </div>
          {selectedCategory && (
            <div className="dialog-categoriesWithModels">
              {categoriesWithModels[selectedCategory].models.map((model) => (
                <button
                  key={model.name}
                  className={`dialog-button ${selectedModel === model.name ? 'selected' : ''}`}
                  onClick={() => handleModelSelect(selectedCategory, model.name)}
                >
                  {model.name}
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