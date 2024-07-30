import axios from 'axios';
import { useState } from 'react';
import { Form, FormControl, InputGroup } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { FaArrowLeft, FaEnvelope, FaLock } from 'react-icons/fa';
import './Login.css';
import Cookies from 'js-cookie';

const LoginForm = () => {
  const navigate = useNavigate();

  const [heading] = useState('Login');

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

  const saveTokenChrome = (token) => {
    if (typeof chrome !== 'undefined' && chrome.storage) {
      chrome.storage.local.set({ jwtToken: token }, function () {
        console.log('Token is saved');
      });
    } else {
      console.error('chrome.storage is not available');
    }
  };

  const saveTokenLocal = (token) => {
    const expiresIn = 24 * 3600; // 1일 = 24시간 * 3600초
    const expiryTime = new Date().getTime() + expiresIn * 1000; // expiresIn은 초 단위
    const tokenData = { token, expiryTime };
    
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('jwtToken', JSON.stringify(tokenData));
      console.log('Token is saved');
    } else {
      console.error('localStorage is not available');
    }
  };

  const onLoginFrm = (e) => {
    e.preventDefault();

    axios.post(
      `${import.meta.env.VITE_API_URL}/api/sign-in`,
      loginFrm,
      {
        headers: {
          "Content-Type": "application/json; charset=utf-8",
        },
        withCredentials: true
      }
    )
      .then(response => {
        localStorage.setItem('username', response.data.username)
        console.log("response:", response);
        const token = response.data.token
        saveTokenLocal(response.data.token);
        saveTokenChrome(token)
        alert('로그인 되었습니다.')

        navigate("/home");
      })
      .catch(error => {
        console.error("Error:", error);
        alert('등록된 회원이 아닙니다.')
      });
  };

  const handleSignUp = () => {
    navigate('/signUp');
  };

  const handleBack = () => {
    navigate(-1);
  };

  return (
    <>
      <button onClick={handleBack} className="nav-button back-button">
        <FaArrowLeft size={20} /> {/* 화살표 아이콘 추가 */}
      </button>
      <div className="login-container">
        <h2 className="login-heading">{heading}</h2>
        <div className="login-box">
          <Form onSubmit={onLoginFrm}>
            <InputGroup className="login-form">
              <InputGroup.Text className="input-icon">
                <FaEnvelope />
              </InputGroup.Text>
              <FormControl
                name="email"
                placeholder="이메일"
                value={email}
                onChange={onChangeFrm}
              />
            </InputGroup>
            <InputGroup className="login-form">
              <InputGroup.Text className="input-icon">
                <FaLock />
              </InputGroup.Text>
              <FormControl
                name="password"
                placeholder="비밀번호"
                type="password"
                value={password}
                onChange={onChangeFrm}
              />
            </InputGroup>
            <div className="text-center">
              <button type="submit" className="login-button">Login</button>
            </div>
          </Form>
          <div className="separator">------------------------- 또는 -------------------------</div>
          <button onClick={handleSignUp} className="login-button">계정등록</button>
        </div>
      </div>
    </>
  );
};

export default LoginForm;
