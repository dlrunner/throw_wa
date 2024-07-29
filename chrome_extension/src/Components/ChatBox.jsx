import React, { useState } from 'react';
import './ChatBox.css';
import { FaSearch } from 'react-icons/fa'; // Font Awesome Search Icon yarn add react-icons
import { ClockLoader } from 'react-spinners'

const ChatBox = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSend = async () => {
    if (input.trim() === '') return;

    setLoading(true);
    setError(null);
    setMessages([]);

    try {
      getTokenLocal(async function (token) {
        if (token) {
          console.log('Token retrieved:', token);

          const responseToken = await fetch(`${import.meta.env.VITE_API_URL}/api/validated_search`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ token: token }),
          });

          if (!responseToken.ok) {
            throw new Error('Token validation failed');
          }

          console.log("responseToken");
          console.log(responseToken);

          const tokenData = await responseToken.json(); // 응답을 JSON으로 파싱
          const { email } = tokenData;  // 구조 분해 할당으로 email 추출
          console.log(email);

          const response = await fetch(`${import.meta.env.VITE_PYTHON_API_URL}/api/search`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: input, top_k: topK, email: email }),  // email을 사용
          });

          if (!response.ok) {
            throw new Error('데이터를 가져올 수 없습니다.');
          }

          const data = await response.json();
          console.log(data);
          const botMessages = data.matches.map(match => ({
            text: '링크',
            sender: 'bot',
            type: match.type,
            link: match.link,
            summary: match.summary,
            title: match.title,
            s3OriginalFilename: match.s3OriginalFilename,
            s3Key: match.s3Key,
            s3Url: match.s3Url
          }));
          console.log(botMessages);

          setMessages(botMessages);
        } else {
          console.log('No token found');
        }
      });
    } catch (error) {
      console.error('Error:', error);
      setError('데이터를 가져오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      handleSend();
    }
  };

  const truncateLink = (text) => {
    const maxLength = 30;
    if (text.length <= maxLength) return text;
    return `${text.substring(0, maxLength)}...`;
  };

  const s3DownloadBtn = async (s3OriginalFilename, s3Key, s3Url) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/download`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ originalFilename: s3OriginalFilename, key: s3Key, url: s3Url }),
      });

      if (!response.ok) {
        throw new Error('Failed to download file');
      }

      // 파일 다운로드 처리
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = s3OriginalFilename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);

    } catch (error) {
      console.error('Error downloading file:', error);
      setError('파일을 다운로드하는데 실패했습니다.');
    }
  };

  // const getTokenChrome = (callback) => {
  //   chrome.storage.local.get(['jwtToken'], function (result) {
  //     callback(result.jwtToken);
  //   });
  // };
  const getTokenLocal = (callback) => {
    if (typeof localStorage !== 'undefined') {
      const tokenData = localStorage.getItem('jwtToken');
      callback(tokenData.token);
    } else {
      console.error('localStorage is not available');
      callback(null);
    }
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
          <button className="search-button" onClick={handleSend}>
            <FaSearch /> {/* 돋보기 아이콘 추가 */}
          </button>
        </div>
      </div>
      {loading && <div className='clock-loader-container'><ClockLoader color="#7289da" size={100} /></div>}
      {error && <div className="error-message">{error}</div>}
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`chat-message ${msg.sender}`}>
            {msg.link ? (
              <>
                <span style={{ fontSize: 'larger' }}>
                  [{msg.type}]
                </span>
                {msg.type === 'PDF' ? (
                  <button onClick={() => s3DownloadBtn(msg.s3OriginalFilename, msg.s3Key, msg.s3Url)} style={{ color: "#9bfe63", background: 'none', border: 'none', padding: 0, cursor: 'pointer', textDecoration: 'underline' }}>
                    {truncateLink(msg.title)}
                  </button>
                ) : (
                  <a href={msg.link} target='_blank' rel='noopener noreferrer' title={msg.link} style={{ color: "#9bfe63" }}>
                    {truncateLink(msg.title)}
                  </a>
                )}
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
