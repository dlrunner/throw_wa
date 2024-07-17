import axios from 'axios';
import React, { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const KakaoLoginHandler = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const handleOAuthKakao = async (code) => {
    try {
      const response = await axios.get(`http://localhost:8080/oauth/login/kakao?code=${code}`);
      const data = response.data;
      alert("로그인 성공: " + data);
      navigate("/home");
    } catch (error) {
      alert("로그인 실패: " + error.message);
      navigate("/fail");
    }
  };

  useEffect(() => {
    const hash = location.hash;
    const searchParams = new URLSearchParams(hash.replace("#", "?"));
    const code = searchParams.get('code');
    if (code) {
      handleOAuthKakao(code);
    } else {
      alert("인증 코드가 없습니다.");
      navigate("/fail");
    }
  }, [location]);

  return (
    <div className="LoginHandler">
      <div className="notice">
        <p>로그인 중입니다.</p>
        <p>잠시만 기다려주세요.</p>
        <div className="spinner"></div>
      </div>
    </div>
  );
}

export default KakaoLoginHandler;
