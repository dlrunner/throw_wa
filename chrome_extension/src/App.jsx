import React from 'react';
import './App.css';
import { Route, Routes } from 'react-router-dom';
import SignUp from './Components/SignUp';
import Login from './Components/Login';
import Home from './Components/Home';
import Onboarding from './Components/OnBorading';
import KakaoLoginHandler from './Components/OAuth/KakaoLoginHandler';

function App() {
  return (
    <>
      <Routes>
        <Route path='/' element={<Onboarding />}></Route>
        <Route path='/home' element={<Home />}></Route>
      </Routes>
    </>
  );
}

export default App;
