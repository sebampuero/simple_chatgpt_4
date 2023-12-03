import React from 'react';
import './ChatSidebar.css'; // Import your CSS file

const ChatSidebar = ({ chats, onChatClick, onDeleteChat }) => {
  const formatDate = (timestamp) => {
    const date = new Date(timestamp * 1000);
    // Format the date as "dd/mm/YYYY hh:mm AM/PM"
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0'); 
    const year = date.getFullYear();
    const hours = date.getHours() % 12 || 12;
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const ampm = date.getHours() >= 12 ? 'PM' : 'AM';
  
    return `${day}/${month}/${year} ${hours}:${minutes} ${ampm}`;
  };

  return (
    <div id="chat-sidebar" className="sidebar">
      <h3>Chats</h3>
      <ul>
        {chats.map((chat) => (
          <li key={chat.timestamp}>
            <div className="chat-row">
              <span className="chat-row-time">{formatDate(chat.timestamp)}</span>
              <span className="chat-row-title" onClick={() => onChatClick(chat.chat_id, chat.timestamp)}>{chat.title}</span>
              <button onClick={() => onDeleteChat(chat.chat_id, chat.timestamp)}><i className="fa-solid fa-trash"></i></button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ChatSidebar;