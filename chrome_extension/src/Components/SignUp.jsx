import React, { useContext, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppContext } from '../contexts/AppContextProvider';
import { Button, Col, Form, FormControl, Row } from 'react-bootstrap'
import axios from 'axios';

const SignUp = () => {
  const navigate = useNavigate();
  const { action: { createMember } } = useContext(AppContext)
  const [frm, setFrm] = useState({
    email: '',
    password: '',
  });

  const { email, password } = frm;

  const onChangeFrm = (e) => {
    console.log("onChangeFrm");
    console.log(e);
    setFrm({
      ...frm,
      [e.target.name]: e.target.value,
    });
  };

  const onSubmitFrm = async (e) => {
    e.preventDefault();
    console.log("onSubmitFrm");
    console.log(e);
    try {
        const response = await axios.post(
            `http://localhost:8080/api/signUp`,
            frm,
            {
                headers: {
                    "Content-Type": "application/json; charset=utf=8",
                },
                withCredentials: true
            }
        );
        console.log("res");
        console.log(response.data);
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
          <Form onSubmit={onSubmitFrm}>
            <FormControl name="email" className='my-3' placeholder='이메일' value={email} onChange={onChangeFrm}></FormControl>
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
