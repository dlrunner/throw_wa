import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const SignUp = () => {
  const [form, setForm] = useState({
    username: '',
    email: '',
    name: '',
    password: '',
    phone: '',
    nickname: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({
      ...form,
      [name]: value,
    });
  };

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${import.meta.env.VITE_API_URL}/signup`, form);
      console.log('회원가입 성공:', response.data);
      navigate('/home');
    } catch (error) {
      console.error('회원가입 오류:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>아이디:</label>
        <input type="text" name="username" value={form.username} onChange={handleChange} required />
      </div>
      <div>
        <label>이메일:</label>
        <input type="email" name="email" value={form.email} onChange={handleChange} required />
      </div>
      <div>
        <label>이름:</label>
        <input type="text" name="name" value={form.name} onChange={handleChange} required />
      </div>
      <div>
        <label>비밀번호:</label>
        <input type="password" name="password" value={form.password} onChange={handleChange} required />
      </div>
      <div>
        <label>휴대폰:</label>
        <input type="tel" name="phone" value={form.phone} onChange={handleChange} required />
      </div>
      <div>
        <label>닉네임:</label>
        <input type="text" name="nickname" value={form.nickname} onChange={handleChange} required />
      </div>
      <button type="submit">회원가입</button>
    </form>
  );
};

export default SignUp;
