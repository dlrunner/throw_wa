import React, { useState } from 'react';
import './ChatBox.css';
import { FaSearch } from 'react-icons/fa'; // Font Awesome Search Icon yarn add react-icons

const ChatBox = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [topK, setTopK] = useState(1);

  const handleSend = () => {
    if (input.trim() === '') return;

    setMessages([]);

    fetch('http://localhost:8000/api/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: input, top_k: topK }),
    })
    .then(response => response.json())
    .then(data => {
      console.log('응답 데이터:', data); // 응답 데이터 확인을 위한 콘솔 출력
      const botMessages = data.matches.map(match => {
        return {
          text: '링크',
          sender: 'bot',
          link: match.link, 
          summary : match.summary
        };
      });
      setMessages(prevMessages => [...prevMessages, ...botMessages]);
    })
    .catch(error => {
      console.error('Error:', error);
    });
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      handleSend();
    }
  };

  const truncateLink = (link) => {
    const maxLength = 30;
    if (link.length <= maxLength) return link;
    return `${link.substring(0, maxLength)}...`;
  };

  return (
    <div className="chat-box">
      <div className="chat-input-container">
      <div className="chat-settings">
          <label>
            
            <input
              type="number"
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
              min="1"
            />
          </label>
        </div>
        <div className="chat-input">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="찾고싶은 링크의 내용을 적어주세요!"
          />
          <button onClick={handleSend}>
            <FaSearch /> {/* 돋보기 아이콘 추가 */}
          </button>
        </div>
      </div>
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`chat-message ${msg.sender}`}>
            {msg.link ? (
              <>
              {msg.text}:<a href={msg.link} target='_blank' rel='noopener noreferrer' title={msg.link}>
                {truncateLink(msg.link)}
              </a>
              <div className='message-summary'>{msg.summary}</div>
              </>
            ) : (
              msg.text
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ChatBox;
