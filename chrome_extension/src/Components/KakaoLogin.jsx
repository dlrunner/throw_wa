import React from 'react'
import { KAKAO_AUTH_URL } from './OAuth/OAuth.js'

const KakaoLogin = () => {

  return (
    <>
      <div>
        <a href={KAKAO_AUTH_URL}>
          <img
            src="https://developers.kakao.com/tool/resource/static/img/button/login/full/ko/kakao_login_medium_narrow.png"
          />
        </a>
      </div>
    </>
  )
}

export default KakaoLogin