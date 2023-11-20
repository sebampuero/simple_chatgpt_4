import React from 'react';
import './ChatSidebar.css'; // Import your CSS file

const ChatSidebar = ({ chats, onChatClick, onDeleteChat }) => {
  return (
    <div id="chat-sidebar" class="sidebar">
      <h3>Chats</h3>
      <ul>
        {chats.map((chat) => (
          <li key={chat.id}>
          <span class="chat-row-title" onClick={() => onChatClick(chat.id)}>{chat.title}</span>
          <button  onClick={() => onDeleteChat(chat.id)}><i class="fa-solid fa-trash"></i></button>
        </li>
        ))}
      </ul>
    </div>
  );
};

export default ChatSidebar;