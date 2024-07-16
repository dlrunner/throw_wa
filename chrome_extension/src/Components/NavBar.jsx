// NavBar.js

import React, { useState } from 'react';
import '../Components/NavBar.css';
import ChatBox from './ChatBox';
import BottomBox from './BottomBox'; // 경로 수정
import '@fortawesome/fontawesome-free/css/all.min.css';

const NavBar = () => {
  const [result, setResult] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showUrlInput, setShowUrlInput] = useState(false);
  const [url, setUrl] = useState('');

  const handleButtonClick = () => {
    setIsLoading(true);
    setResult('마킹중!');

    chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
      const url = tabs[0].url;

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
              throw new Error('오류발생' + text);
            });
          }
          return response.json();
        })
        .then(data => {
          if (data.success) {
            setResult('throw-wa에 저장되었습니다!');
          } else {
            throw new Error(data.message || '처리 실패');
          }
        })
        .catch(error => {
          setResult('오류 발생: ' + error.message);
        })
        .finally(() => {
          setIsLoading(false);
          setTimeout(() => setResult(''), 3000); // 3초 후에 result 메시지 지우기
        });
    });
  };

  const handleUrlSave = () => {
    setIsLoading(true);
    setResult('마킹중');

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
            throw new Error('오류발생:'+ text);
          });
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          setResult('throw-wa에 저장되었습니다!');
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

  return (
    <div className="nav-bar-container">
      <h2>Throw-Wa Service</h2>
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
              마킹
            </button>
          </>
        ) : (
          <button className="nav-button" onClick={handleButtonClick} disabled={isLoading}>
            현재 탭 마킹
          </button>
        )}
        <div className="result-div" id="result">{result}</div>
      </div>
      <div className="chat-box-container">
        <ChatBox />
      </div>
      <div className='bottom-box-container'>
      <BottomBox /> {/* BottomBox 컴포넌트 추가 */}
      </div>
    </div>
  );
};

export default NavBar;
