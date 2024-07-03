import { useState } from 'react'
import './App.css'
import styled from 'styled-components';
import KakaoLogin from './Components/KakaoLogin';
import ChatWindow from './Components/ChatWindow';
import NavBar from './Components/NavBar';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
`;

function App() {

  return (
    <>
      <KakaoLogin />
      <Container>
        <NavBar />
        <ChatWindow />
      </Container>
    </>
  )
}

export default App
