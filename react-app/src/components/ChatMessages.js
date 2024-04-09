import React, { useState } from 'react';
import './ChatMessages.css';

const ChatMessages = ({ messages }) => {
  const [showModal, setShowModal] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);

  const openModal = (image) => {
    setSelectedImage(image);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedImage(null);
  };

  return (
    <div id="chat-messages">
      {messages.map((message) => (
        <div key={message.timestamp} className={`message-bubble ${message.role === 'user' ? 'user-message' : 'peer-message'}`}>
          {message.image && message.image !== null && (
            <img src={message.image} alt="GPT4-V image prompt" onClick={() => openModal(message.image)} />
          )}
          <span>
            {message.content}
            {message.role !== 'user' && (
              <>
                <br></br>
                <br></br>
                <span style={{ fontWeight: 'bold', fontSize: '0.8em' }}>
                  {message.language_model}
                </span>
              </>
            )}
          </span>
        </div>
      ))}

      {showModal && (
        <div className="modal" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <img src={selectedImage} alt="Enlarged GPT4-V image prompt" />
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatMessages;