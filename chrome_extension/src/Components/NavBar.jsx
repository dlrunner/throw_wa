import React, { useState } from 'react';
import '../Components/NavBar.css';

const NavBar = () => {
  const [result, setResult] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleButtonClick = () => {
    // 버튼 비활성화 및 로딩 메시지 표시
    setIsLoading(true);
    setResult('처리 중...');

    // Chrome 확장 프로그램의 현재 활성 탭 URL 가져오기
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
            console.error('응답 텍스트:', text); // 응답이 HTML인지 확인하기 위해 텍스트 출력
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
    </div>
  );
};

export default NavBar;
