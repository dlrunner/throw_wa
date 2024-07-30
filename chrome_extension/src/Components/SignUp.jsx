import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, FormControl, InputGroup } from 'react-bootstrap';
import { FaArrowLeft } from 'react-icons/fa';
import axios from 'axios';
import './SignUp.css';

const SignUp = () => {
  const navigate = useNavigate();

  const [signFrm, setSignFrm] = useState({
    email: '',
    password: '',
    name: ''
  });

  const { email, password, name } = signFrm;

  const onChangeFrm = (e) => {
    setSignFrm({
      ...signFrm,
      [e.target.name]: e.target.value,
    });
  };

  const onSignFrm = async (e) => {
    e.preventDefault();
    try {
      await axios.post(
        `${import.meta.env.VITE_API_URL}/api/sign-up`,
        signFrm,
        {
          headers: {
            "Content-Type": "application/json; charset=utf=8",
          },
          withCredentials: true
        }
      ).then(() => {
        alert(`회원가입이 완료되었습니다. ${name}님`);
        navigate("/login");
      });
    } catch (error) {
      console.error("Error:", error);
    }
  };

  const handleBack = () => {
    navigate(-1);
  };

  return (
    <>
      <button onClick={handleBack} className="nav-button back-button">
        <FaArrowLeft size={20} />
      </button>
      <div className="sign-up-container">
        <h2 className="sign-up-title">계정등록</h2>
        <div className="sign-up-box">
          <Form onSubmit={onSignFrm}>
            <InputGroup className="sign-up-form">
              <FormControl
                name="email"
                type="email"
                placeholder="이메일"
                value={email}
                onChange={onChangeFrm}
              />
            </InputGroup>
            <InputGroup className="sign-up-form">
              <FormControl
                name="password"
                type="password"
                placeholder="비밀번호"
                value={password}
                onChange={onChangeFrm}
              />
            </InputGroup>
            <InputGroup className="sign-up-form">
              <FormControl
                name="name"
                placeholder="이름"
                value={name}
                onChange={onChangeFrm}
              />
            </InputGroup>
            <div className="text-center">
              <button type="submit" className="sign-up-button">등록</button>
            </div>
          </Form>
          <button onClick={() => navigate("/login")} className="sign-up-button">로그인</button>
        </div>
      </div>
    </>
  );
};

export default SignUp;
