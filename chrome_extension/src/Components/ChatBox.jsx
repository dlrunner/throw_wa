import React, { useState } from 'react';
import './ChatBox.css'; // 경로 수정

const ChatBox = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [topK, setTopK] = useState(1);

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
      body: JSON.stringify({ text: input, top_k: topK }),
    })
    .then(response => response.json())
    .then(data => {
      const botMessages = data.matches.map(match => {
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

  const truncateLink = (link) => {
    const maxLength = 30;
    if (link.length <= maxLength) return link;
    return `${link.substring(0, maxLength)}...`;
  };

  return (
    <div className="chat-box">
      <div className="chat-settings">
        <label>
          범위:
          <input
            type="number"
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
            min="1"
          />
        </label>
      </div>
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`chat-message ${msg.sender}`}>
            {msg.link ? (
              <>
              {msg.text}:<a href={msg.link} target='_blank' rel='noopener noreferrer' title={msg.link}>
                {truncateLink(msg.link)}
              </a>
              </>
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
          placeholder="뭐였더라..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
};

export default ChatBox;
