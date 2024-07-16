import axios from 'axios';
import React, { useState } from 'react';
import { Form, FormControl } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { KAKAO_AUTH_URL } from './OAuth/OAuth';


const LoginForm = () => {
  const navigate = useNavigate();

  const [loginFrm, setLoginFrm] = useState({
    email: '',
    password: '',
  });

  const { email, password } = loginFrm;

  const onChangeFrm = (e) => {
    setLoginFrm({
      ...loginFrm,
      [e.target.name]: e.target.value,
    });
  };

  const onLoginFrm = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/api/login`,
        loginFrm,
        {
          headers: {
            "Content-Type": "application/json; charset=utf=8",
          },
          withCredentials: true
        }
      );
      console.log("response:", response.data);
    } catch (error) {
      console.error("Error:", error);
    }
  }

  const onSocialLoginBtnHandler = () => {
    window.location.href = `${import.meta.env.VITE_API_URL}/oauth/kakao`;
  }

  const handleSignUp = () => {
    navigate('/signUp');
  };

  const handleHome = () => {
    navigate('/Home');
  };

  return (
    <div className="login-container">
      <img src="/logo/logo.png" className="logo-img" alt="Owl Logo" />
      <div className="login-box">
        <h2>Login</h2>
        <Form onSubmit={onLoginFrm}>
          <FormControl
            name="email"
            className='form-control'
            placeholder='이메일'
            value={email}
            onChange={onChangeFrm}
          />
          <FormControl
            name="password"
            className='form-control'
            placeholder='비밀번호'
            type='password'
            value={password}
            onChange={onChangeFrm}
          />
          <button type="submit" className="submit-button">로그인</button>
        </Form>
        <button onClick={handleSignUp} className="sign-up-button">회원가입</button>
        <button onClick={handleHome} className="home-button">홈으로</button>
      </div>
      <div className='kakao-sign-in-btn' onClick={onSocialLoginBtnHandler}>
        <img
          src="https://developers.kakao.com/tool/resource/static/img/button/login/full/ko/kakao_login_medium_narrow.png"
          alt="Kakao Login"
        />
      </div>
    </div>
  );
};

export default LoginForm;
