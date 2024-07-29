import axios from 'axios';
import { useEffect, useState } from 'react';
import { Form, FormControl } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import './Login.css';
import Cookies from 'js-cookie';

const LoginForm = () => {
  const navigate = useNavigate();

  const [heading, setHeading] = useState('아직 회원이 아니신가요?');
  const [fade, setFade] = useState(false);

  useEffect(() => {
    const headings = ['아직 회원이 아니신가요?', '링크 찾기를 더 쉽게!', 'Throw-wa!'];
    let index = 0;

    const interval = setInterval(() => {
      setFade(true);
      setTimeout(() => {
        index = (index + 1) % headings.length;
        setHeading(headings[index]);
        setFade(false);
      }, 500);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const [loginFrm, setLoginFrm] = useState({
    email: '',
    password: '',
  });

  const { email, password } = loginFrm;

  const onChangeFrm = (e) => {
    console.log("onChangeFrm:", e);
    setLoginFrm({
      ...loginFrm,
      [e.target.name]: e.target.value,
    });
  };

  // const saveTokenChrome = (token) => {
  //   if (typeof chrome !== 'undefined' && chrome.storage) {
  //     chrome.storage.local.set({ jwtToken: token }, function () {
  //       console.log('Token is saved');
  //     });
  //   } else {
  //     console.error('chrome.storage is not available');
  //   }
  // };
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
    console.log("onLoginFrm:", e);

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
        console.log("response:", response);
        saveTokenLocal(response.data.token);

        navigate("/home");
      })
      .catch(error => {
        console.error("Error:", error);
      });
  };

  const handleSignUp = () => {
    navigate('/signUp')
  };

  return (
    <>
      <div className="login-container">
        <div className="login-box">
          <h2 className={`login-heading ${fade ? 'out' : 'in'}`}>{heading}</h2>
          <Form onSubmit={onLoginFrm}>
            <FormControl
              name="email"
              className='login-form'
              placeholder='이메일'
              value={email}
              onChange={onChangeFrm}
            />
            <FormControl
              name="password"
              className='login-form'
              placeholder='비밀번호'
              type="password"
              value={password}
              onChange={onChangeFrm}
            />
            <div className='text-center'>
              <button type="submit" className="login-button">로그인</button>
            </div>
          </Form>
          <button onClick={handleSignUp} className="login-button">회원가입</button>
        </div>
      </div>
    </>
  );
};

export default LoginForm;
