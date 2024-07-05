import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

const KakaoLoginHandler = (props) => {
  const navigate = useNavigate();
  const code = new URL(window.location.href).searchParams.get("code");
  console.log(code);

  // 인가코드 -> 백단
  useEffect(() => {
    const kakaoLoginCertification = async () => {
      await axios({
        method: "GET",
        url: `${import.meta.env.VITE_API_URL}/api/oauth2/callback/kakao?code=${code}`,
        headers: {
          "Content-Type": "application/json;charset=utf-8", // json형태로 데이터를 보내는 코드
          "Access-Control-Allow-Origin": "*" // CORS 인증 코드, 프로젝트 url에 맞게 수정해야함
        },
      }).then((res) => {
        console.log(res);
        // 로컬에 저장
        localStorage.setItem("name", res.data.account.kakaoName);
        // 토큰도 받았겠다 로그인 됐으니 메인으로 화면 전환
        navigate("/home")
      })
    };
    kakaoLoginCertification()
  }, [props.history]);

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
