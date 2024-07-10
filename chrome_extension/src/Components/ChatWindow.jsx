import React from 'react';
import styled from 'styled-components';

const ChatContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid #ccc;
  margin: 10px;
`;

const Messages = styled.div`
  flex: 1;
  padding: 10px;
  overflow-y: auto;
`;

const ChatInput = styled.div`
  display: flex;
  padding: 10px;
  border-top: 1px solid #ccc;
`;

const Input = styled.input`
  flex: 1;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-right: 10px;
`;

const SendButton = styled.button`
  padding: 10px 20px;
  background-color: #333;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  &:hover {
    background-color: #555;
  }
`;

const ChatWindow = () => {
  return (
    <ChatContainer>
      <Messages>
        {/* 여기에 채팅 메시지가 렌더링 됩니다 */}
      </Messages>
      <ChatInput>
        <Input type="text" placeholder="Type your message..." />
        <SendButton>Send</SendButton>
      </ChatInput>
    </ChatContainer>
  );
};

export default ChatWindow;
