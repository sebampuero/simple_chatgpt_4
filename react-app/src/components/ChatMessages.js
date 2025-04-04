import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
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
            <img src={message.image} onClick={() => openModal(message.image)} />
          )}
          <span>
            <ReactMarkdown>{message.content}</ReactMarkdown>
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
            <img src={selectedImage} />
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatMessages;