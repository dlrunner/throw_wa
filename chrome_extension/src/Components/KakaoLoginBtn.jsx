import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleEmailChange = (e) => {
    setEmail(e.target.value);
  };

  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle login logic here
    console.log('Email:', email);
    console.log('Password:', password);
  };
  const handleSignUp = () => {
    navigate('/signUp')
  };
  const handleHome = () => {
    navigate('/Home')
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '20px' }}>
      <img src="/logo/logo.png" style={{ width: '150px', height: 'auto', marginBottom: '20px' }} />
    <div style={{ maxWidth: '400px', margin: 'auto', padding: '1em', border: '1px solid #ccc', borderRadius: '15px' }}>
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '1em' }}>
          <label htmlFor="email" style={{ display: 'block', marginBottom: '.5em' }}>Email</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={handleEmailChange}
            style={{ width: '100%', padding: '.5em', boxSizing: 'border-box' }}
            required
          />
        </div>
        <div style={{ marginBottom: '1em' }}>
          <label htmlFor="password" style={{ display: 'block', marginBottom: '.5em' }}>Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={handlePasswordChange}
            style={{ width: '100%', padding: '.5em', boxSizing: 'border-box' }}
            required
          />
        </div>
        <button type="submit" style={{ width: '100%', padding: '.5em', background: '#007bff', color: '#fff', border: 'none', borderRadius: '5px' }}>로그인</button>
      </form>
      <button onClick={handleSignUp} style={{ width: '100%', padding: '.5em', background: '#007bff', color: '#fff', border: 'none', borderRadius: '5px', marginTop: '10px'}}>회원가입</button>
      <button onClick={handleHome} style={{ width: '100%', padding: '.5em', background: '#007bff', color: '#fff', border: 'none', borderRadius: '5px', marginTop: '10px'}}>홈으로</button>
      <div>
        <a href='{http://localhost:8080/oauth2/authorization/kakao}'>
          <img
            src="https://developers.kakao.com/tool/resource/static/img/button/login/full/ko/kakao_login_medium_narrow.png"
          />
        </a>
      </div>
    </div>
    </div>
  );
};

export default LoginForm;