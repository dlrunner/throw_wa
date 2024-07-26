import axios from 'axios';
import { useState } from 'react';
import { Form, FormControl, InputGroup } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { FaArrowLeft, FaEnvelope, FaLock } from 'react-icons/fa';
import './Login.css';

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

  const saveToken = (token) => {
    if (typeof chrome !== 'undefined' && chrome.storage) {
      chrome.storage.local.set({ jwtToken: token }, function() {
        console.log('Token is saved');
      });
    } else {
      console.error('chrome.storage is not available');
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
        saveToken(response.data.token);

        navigate("/home");
      })
      .catch(error => {
        console.error("Error:", error);
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
