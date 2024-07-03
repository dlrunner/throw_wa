import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

const KakaoLoginHandler = (props) => {
  const navigate = useNavigate();
  const code = new URL(window.location.href).searchParams.get("code");

  // 인가코드 백으로 보내는 코드
  useEffect(() => {
    const kakaoLogin = async () => {
      await axios({
        method: "GET",
        url: `${OAuth.env.REDIRECT_URI}/?code=${code}`,
        headers: {
          "Content-Type": "application/json;charset=utf-8",
          "Access-Control-Allow-Origin": "*" // CORS 에러 때문에 넣은 것, 해결 시 삭제할 것
        }
      }).then((res) => {
        console.log(res);
        // 계속 쓸 정보들은 localStorage에 저장(ex: 이름)
        localStorage.setItem("name", res.data.account.kakaoName);
        // 로그인 성공 시 이동할 페이지
        navigate("/ThrowWa");
      })
    }
    kakaoLogin();
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
