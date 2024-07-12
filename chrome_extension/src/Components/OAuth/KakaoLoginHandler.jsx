import React, { useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useCookies } from 'react-cookie'

const KakaoLoginHandler = () => {

  const { token, expirationTime } = useParams();
  const [cookie, setCookie] = useCookies();
  const navigate = useNavigate();
  const code = new URL(window.location.href).searchParams.get("code");
  console.log(code);

  // 인가코드 -> 백단
  useEffect(() => {

    if (!token || !expirationTime) return;

    const now = (new Date().getTime()) * 1000;
    const expires = new Date(now + Number(expirationTime));

    setCookie('accessToken', token, {expires, path: '/'});

    navigate("/home")

  }, [token]);

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
