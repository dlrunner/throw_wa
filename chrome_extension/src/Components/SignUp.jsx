import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Col, Form, FormControl, Row } from 'react-bootstrap'
import axios from 'axios';

const SignUp = () => {
  const navigate = useNavigate();

  const [signFrm, setSignFrm] = useState({
    email: '',
    password: '',
  });

  const { email, password } = signFrm;

  const onChangeFrm = (e) => {
    // console.log("onChangeFrm", e);
    setSignFrm({
      ...signFrm,
      [e.target.name]: e.target.value,
    });
  };

  const onSignFrm = async (e) => {
    e.preventDefault();
    // console.log("onSignFrm", e);
    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/api/signUp`,
        signFrm,
        {
          headers: {
            "Content-Type": "application/json; charset=utf=8",
          },
          withCredentials: true
        }
      ).then(
        navigate("/home")
      );
      // console.log("response", response.data);
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <>
      <Row>
        <Col>
          <h1>회원가입</h1>
        </Col>
      </Row>
      <Row>
        <Col>
          <Form onSubmit={onSignFrm}>
            <FormControl name="email" className='my-3' placeholder='email' value={email} onChange={onChangeFrm}></FormControl>
            <FormControl name="password" className='my-3' placeholder='비밀번호' value={password} onChange={onChangeFrm}></FormControl>
            <div className='text-center'>
              <Button type="submit" className='me-3'>등록</Button>
              <Button variant='secondary'>취소</Button>
            </div>
          </Form>
        </Col>
      </Row>
    </>
  );
};

export default SignUp;
