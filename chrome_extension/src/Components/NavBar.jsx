import React, { useState } from 'react';
import '../Components/NavBar.css';
import ChatBox from './ChatBox';

const NavBar = () => {
  const [result, setResult] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleButtonClick = () => {
    setIsLoading(true);
    setResult('처리 중...');

    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      const url = tabs[0].url;

      fetch('http://localhost:8080/api/url', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({url: url}),
      })
      .then(response => {
        if (!response.ok) {
          return response.text().then(text => {
            console.error('응답 텍스트:', text);
            throw new Error('API 호출 실패: ' + response.status + ', ' + text);
          });
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          setResult('북마크에 저장되었습니다.');
        } else {
          throw new Error(data.message || '처리 실패');
        }
      })
      .catch(error => {
        console.error('오류 발생:', error);
        setResult('오류 발생: ' + error.message);
      })
      .finally(() => {
        setIsLoading(false);
      });
    });
  };

  return (
    <div className="nav-bar-container">
      <button className="nav-button" onClick={handleButtonClick} disabled={isLoading}>
        {isLoading ? '처리 중...' : '저장'}
      </button>
      <div className="result-div" id="result">{result}</div>
      <ChatBox />
    </div>
  );
};

export default NavBar;
