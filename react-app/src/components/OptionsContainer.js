import React from 'react';

const OptionsContainer = ({ optionsVisible, toggleSidebar, newChat, handleImageUpload, selectedModel, selectModel, sidebarVisible }) => {
  
    return (
      <div id="options-container" className={optionsVisible ? 'show' : 'hidden'}>
        <div id="options-header">Options</div>
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
        {selectedModel === 'GPT4' && (
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
        )}
        <div>
          <button
            id="gemini-button"
            className={`custom-file-upload ${selectedModel === 'Gemini' ? 'selected' : ''}`}
            onClick={() => selectModel('Gemini')}
          >
            Gemini
          </button>
        </div>
        <div>
          <button
            id="gpt4-button"
            className={`custom-file-upload ${selectedModel === 'GPT4' ? 'selected' : ''}`}
            onClick={() => selectModel('GPT4')}
          >
            GPT4
          </button>
        </div>
        <div>
          <button
            id="mistral-button"
            className={`custom-file-upload ${selectedModel === 'Mistral' ? 'selected' : ''}`}
            onClick={() => selectModel('Mistral')}
          >
            Mistral
          </button>
        </div>
        <div>
          <button
            id="mistral-button"
            className={`custom-file-upload ${selectedModel === 'Claude' ? 'selected' : ''}`}
            onClick={() => selectModel('Claude')}
          >
            Claude
          </button>
        </div>
      </div>
    );
  };

  export default OptionsContainer;