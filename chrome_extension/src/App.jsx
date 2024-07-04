import React, { useState, useEffect } from 'react'
import './App.css'
import styled from 'styled-components';
import { Link, Route, Routes } from 'react-router-dom';
import SignUp from './Components/SignUp';
import KakaoLoginBtn from './Components/KakaoLoginBtn';
import Home from './Components/Home';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
`;

function App() {
  const API_URL = import.meta.env.VITE_API_URL;

  return (
    <>
    <nav>
      <Link to="/signUp">signUp</Link>
      <Link to="/login">login</Link>
      <Link to="/home">home</Link>
    </nav>
      <Routes>
        <Route path='/signUp' element={<SignUp />}></Route>
        <Route path='/login' element={<KakaoLoginBtn />}></Route>
        <Route path='/home' element={<Home />}></Route>
      </Routes>
    </>
  )
}

export default App
