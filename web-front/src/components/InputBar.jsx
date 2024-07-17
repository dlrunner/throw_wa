import { useState } from "react";
import './css/InputBar.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
import { FaSearch } from 'react-icons/fa';

function InputBar() {
  const [result, setResult] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showUrlInput, setShowUrlInput] = useState(false);
  const [url, setUrl] = useState('');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [topK, setTopK] = useState(1);

  const handleUrlSave = () => {
    setIsLoading(true);
    setResult('북마크에 넣는중!');

    fetch('http://localhost:8080/api/url', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: url }),
    })
      .then(response => {
        if (!response.ok) {
          return response.text().then(text => {
            throw new Error('오류발생:' + text);
          });
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          setResult('북마크에 저장되었습니다!');
        } else {
          throw new Error(data.message || '처리 실패');
        }
      })
      .catch(error => {
        setResult('오류 발생: ' + error.message);
      })
      .finally(() => {
        setIsLoading(false);
        setShowUrlInput(false); // URL 입력란 숨기기
        setUrl(''); // URL 입력값 초기화
        setTimeout(() => setResult(''), 3000); // 3초 후에 result 메시지 지우기
      });
  };

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
    <>
      <div className="logo">
        <h1>Throw WA</h1>
      </div>
      <div className="nav-bar-container">
        <div className="nav-bar-actions">
          <button className="fas-button" onClick={() => setShowUrlInput(!showUrlInput)}>
            <i className="fas fa-sync-alt"></i> {/* 전환 아이콘 추가 */}
          </button>
          {isLoading ? (
            <div className="loading-bar"></div>
          ) : showUrlInput ? (
            <>
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="URL 입력"
                className="url-input"
              />
              <button className="nav-button" onClick={handleUrlSave} disabled={isLoading}>
                북마크
              </button>
            </>
          ) : (
            <>
              <input
                type="number"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                min="1"
                className="topK-input"
              />
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="뭐였더라..."
                className="search-input"
              />
              <button className="nav-button" onClick={handleSend}>
                <FaSearch /> {/* 돋보기 아이콘 추가 */}
              </button>
            </>
          )}
        </div>
      </div>
    </>
  );
}

export default InputBar