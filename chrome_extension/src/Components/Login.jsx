import axios from 'axios';
import { useState } from 'react';
import { Form, FormControl } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { useCookies } from 'react-cookie';

const LoginForm = () => {
  const navigate = useNavigate();

  const [loginFrm, setLoginFrm] = useState({
    email: '',
    password: '',
  });

  const [cookie, setCookie] = useCookies();

  const { email, password } = loginFrm;

  const onChangeFrm = (e) => {
    console.log("onChangeFrm:", e);
    setLoginFrm({
      ...loginFrm,
      [e.target.name]: e.target.value,
    });
  };

  const onLoginFrm = async (e) => {
    e.preventDefault();
    console.log("onLoginFrm:", e);
    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/api/sign-in`,
        loginFrm,
        {
          headers: {
            "Content-Type": "application/json; charset=utf=8",
          },
          withCredentials: true
        }
      );      
      console.log("response:", response);
      const now = (new Date().getTime()) * 1000
      const expires = new Date(now + response.data.expirationTime)
      setCookie('accessToken', response.data.token, { expires, path: '/' })
      navigate("/home")
    } catch (error) {
      console.error("Error:", error);
    }
  }

  const onSocialLoginBtnHandler = () => {
    window.location.href = `${import.meta.env.VITE_API_URL}/api/oauth/kakao`;
  }

  const handleSignUp = () => {
    navigate('/signUp')
  };
  const handleHome = () => {
    navigate('/Home')
  };

  return (
    <>
      <div style={{ textAlign: 'center', marginTop: '20px' }}>
        <img src="/logo/logo.png" style={{ width: '150px', height: 'auto', marginBottom: '20px' }} />
        <div style={{ maxWidth: '400px', margin: 'auto', padding: '1em', border: '1px solid #ccc', borderRadius: '15px' }}>
          <h2>Login</h2>
          <Form onSubmit={onLoginFrm}>
            <FormControl name="email" className='my-3' placeholder='이메일' value={email} onChange={onChangeFrm}></FormControl>
            <FormControl name="password" className='my-3' placeholder='비밀번호' value={password} onChange={onChangeFrm}></FormControl>
            <div className='text-center'>
              <button type="submit" style={{ width: '100%', padding: '.5em', background: '#007bff', color: '#fff', border: 'none', borderRadius: '5px' }}>로그인</button>
            </div>
          </Form>
          <button onClick={handleSignUp} style={{ width: '100%', padding: '.5em', background: '#007bff', color: '#fff', border: 'none', borderRadius: '5px', marginTop: '10px' }}>회원가입</button>
          <button onClick={handleHome} style={{ width: '100%', padding: '.5em', background: '#007bff', color: '#fff', border: 'none', borderRadius: '5px', marginTop: '10px' }}>홈으로</button>
        </div>
      </div>
      <div>
        <button className="kakao-sign-in-btn" onClick={onSocialLoginBtnHandler} style={{ border: 'none', background: 'none', padding: 0 }}>
          <img
            src="https://developers.kakao.com/tool/resource/static/img/button/login/full/ko/kakao_login_medium_narrow.png"
          />
        </button>
      </div>
    </>
  );
};

export default LoginForm;