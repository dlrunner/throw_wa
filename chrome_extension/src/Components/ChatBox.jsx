import React, { useState } from 'react';
import './ChatBox.css';  // 경로 수정

const ChatBox = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() === '') return;

    const userMessage = { text: input, sender: 'user' };
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setInput('');

    fetch('http://localhost:8000/api/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: input, top_k: 3 }),
    })
    .then(response => response.json())
    .then(data => {
      console.log('API response:', data);
      const botMessages = data.matches.map(match => {
        console.log('Link:', match.link ? match.link : 'No link');
        return {
          text: '링크',
          sender: 'bot',
          link: match.link
        };
      });
      setMessages(prevMessages => [...prevMessages, ...botMessages]);
    })
    .catch(error => {
      console.error('Error:', error);
    });
  };

  return (
    <div className="chat-box">
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`chat-message ${msg.sender}`}>
            {msg.link ? (
              <a href={msg.link} target='_blank' rel='noopener noreferrer'>
                {msg.text}: {msg.link}
              </a>
            ) : (
              msg.text
            )}
          </div>
        ))}
      </div>
      <div className="chat-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
};

export default ChatBox;
