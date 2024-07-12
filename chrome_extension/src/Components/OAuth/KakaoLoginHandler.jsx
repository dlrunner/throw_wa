import axios from 'axios';
import React, { useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

const KakaoLoginHandler = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const handleOAuthKakao = async (code) => {
    try {
      // 카카오로부터 받아온 code를 서버에 전달하여 카카오로 회원가입 & 로그인한다
      const response = await axios.get(`http://localhost:8080/oauth/login/kakao?code=${code}`);
      const data = response.data; // 응답 데이터
      alert("로그인 성공: " + data)
      // navigate("/success");
    } catch (error) {
      // navigate("/fail");
    }
  }

  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const code = searchParams.get('code');  // 카카오는 Redirect 시키면서 code를 쿼리 스트링으로 준다.
    if (code) {
      // alert("CODE = " + code);
      handleOAuthKakao(code);
      navigate("/home");
    }
  }, [location]);

  return (
    <>
      <div className="LoginHandeler">
        <div className="notice">
          <p>로그인 중입니다.</p>
          <p>잠시만 기다려주세요.</p>
          <div className="spinner"></div>
        </div>
      </div>
    </>
  )
}

export default KakaoLoginHandler
