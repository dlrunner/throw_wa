import React, { useEffect, useState } from 'react';
import '../Components/NavBar.css';
import ChatBox from './ChatBox';
import BottomBox from './BottomBox';
import '@fortawesome/fontawesome-free/css/all.min.css';
import MetamaskLogo from './MetamaskLogo';
import { BeatLoader } from 'react-spinners';
import { CSSTransition } from 'react-transition-group';

const NavBar = () => {
  const [result, setResult] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showUrlInput, setShowUrlInput] = useState(false);
  const [url, setUrl] = useState('');
  const [heading, setHeading] = useState('Throw-wa Service');
  const [fade, setFade] = useState(false);
  const [file, setFile] = useState(null);

  useEffect(() => {
    const headings = ['Throw-wa Service', '회원님들의 시간은 소중하니까..', '생각나는 키워드를 입력해보세요!'];
    let index = 0;

    const interval = setInterval(() => {
      setFade(true);
      setTimeout(() => {
        index = (index + 1) % headings.length;
        setHeading(headings[index]);
        setFade(false);
      }, 500); // 500ms의 페이드 아웃 시간
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const getToken = (callback) => {
    chrome.storage.local.get(['jwtToken'], function (result) {
      callback(result.jwtToken);
    });
  };

  const handleButtonClick = async () => {
    setIsLoading(true);

    chrome.tabs.query({ active: true, currentWindow: true }, async function (tabs) {
      const url = tabs[0].url;

      getToken(async function (token) {
        if (token) {
          console.log('Token retrieved:', token);
          try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/url`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ url: url, token: token }),
            });

            if (!response.ok) {
              const text = await response.text();
              throw new Error('오류발생' + text);
            }

            const data = await response.json();
            if (data.success) {
              setResult('throw-wa에 저장되었습니다!');
            } else {
              throw new Error(data.message || '처리 실패');
            }
          } catch (error) {
            setResult('오류 발생: ' + error.message);
          } finally {
            setIsLoading(false);
            setTimeout(() => setResult(''), 3000); // 3초 후에 result 메시지 지우기
          }
        } else {
          console.log('No token found');
          setIsLoading(false);
          setResult('토큰을 찾을 수 없습니다.');
          setTimeout(() => setResult(''), 3000); // 3초 후에 result 메시지 지우기
        }
      });
    });
  };

  const handleUrlSave = async () => {
    setIsLoading(true);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/url`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url }),
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error('오류발생:' + text);
      }

      const data = await response.json();
      if (data.success) {
        setResult('throw-wa에 저장되었습니다!');
      } else {
        throw new Error(data.message || '처리 실패');
      }
    } catch (error) {
      setResult('오류 발생: ' + error.message);
    } finally {
      setIsLoading(false);
      setShowUrlInput(false); // URL 입력란 숨기기
      setUrl(''); // URL 입력값 초기화
      setTimeout(() => setResult(''), 3000); // 3초 후에 result 메시지 지우기
    }
  };

  const handleFileUpload = async () => {
    if (!file) {
      setResult('파일을 선택해 주세요.');
      setTimeout(() => setResult(''), 3000);
      return;
    }

    setIsLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    getToken(async function (token) {
      if (token) {
        console.log('Token retrieved:', token);
        try {
          formData.append('token', token);
          const response = await fetch(`${import.meta.env.VITE_API_URL}/api/FileUpload`, {
            method: 'POST',
            body: formData,
          });

          if (!response.ok) {
            const text = await response.text();
            throw new Error('오류발생: ' + text);
          }

          const data = await response.json();
          if (data.success) {
            setResult('파일이 성공적으로 업로드되었습니다!');
          } else {
            throw new Error(data.message || '처리 실패');
          }
        } catch (error) {
          setResult('오류 발생: ' + error.message);
        } finally {
          setIsLoading(false);
          setFile(null); // 파일 선택 초기화
          setTimeout(() => setResult(''), 3000); // 3초 후에 result 메시지 지우기
        }
      } else {
        console.log('No token found');
        setIsLoading(false);
        setResult('토큰을 찾을 수 없습니다.');
        setTimeout(() => setResult(''), 3000); // 3초 후에 result 메시지 지우기
      }
    });
  };

  return (
    <div className="nav-bar-container">
      <MetamaskLogo />
      <h2 className={`fade ${fade ? 'out' : 'in'}`}>{heading}</h2>
      <div className="nav-bar-actions">
        <button className="fas-button" onClick={() => setShowUrlInput(!showUrlInput)}>
          <i className="fas fa-sync-alt"></i> {/* 전환 아이콘 추가 */}
        </button>
        {isLoading ? (
          <div className='clock-loader-container-narvar'><BeatLoader color="#7289da" size={20} /></div>
        ) : (
          <>
            <CSSTransition
              in={showUrlInput}
              timeout={600}  // 애니메이션 시간을 600ms로 설정
              classNames="url-input"
              unmountOnExit
            >
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="URL 입력"
                className="url-input"
              />
            </CSSTransition>
            {showUrlInput && (
              <button className="nav-button" onClick={handleUrlSave} disabled={isLoading}>
                마킹
              </button>
            )}
          </>
        )}
        {!showUrlInput && !isLoading && (
          <button className="nav-button" onClick={handleButtonClick} disabled={isLoading}>
            현재 탭 마킹
          </button>
        )}
        <div className="file-upload-container">
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files[0])}
            className="file-input"
          />
          <button className="nav-button" onClick={handleFileUpload} disabled={isLoading}>
            PDF 업로드
          </button>
        </div>
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
