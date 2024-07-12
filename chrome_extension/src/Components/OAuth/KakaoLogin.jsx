import React from 'react'
import axios from 'axios'

const KakaoLogin = () => {

  // const kakaoLoginCertification = async () => {
  //   await axios({
  //     method: "GET",
  //     url: `${import.meta.env.VITE_API_URL}/api/oauth2/kakao`,
  //     headers: {
  //       "Content-Type": "application/json;charset=utf-8", // json형태로 데이터를 보내는 코드
  //       "Access-Control-Allow-Origin": "*" // CORS 인증 코드, 프로젝트 url에 맞게 수정해야함
  //     },
  //   }).then((res) => {
  //     console.log(res);
  //     // 로컬에 저장
  //     localStorage.setItem("name", res.data.account.kakaoName);
  //     // 토큰도 받았겠다 로그인 됐으니 메인으로 화면 전환
  //     navigate("/home")
  //   })
  // };
  // kakaoLoginCertification()

  return (
    <>
      {/* <div>
        <a href='{http://localhost:8080/oauth2/authorization/kakao}'>
          <img
            src="https://developers.kakao.com/tool/resource/static/img/button/login/full/ko/kakao_login_medium_narrow.png"
          />
        </a>
      </div> */}
    </>
  )
}

export default KakaoLogin