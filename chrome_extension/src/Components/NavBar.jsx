import React from 'react';
import styled from 'styled-components';

const NavBarContainer = styled.div`
  display: flex;
  justify-content: space-around;
  background-color: #333;
  padding: 10px;
`;

const NavButton = styled.button`
  background-color: #444;
  color: white;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
  &:hover {
    background-color: #555;
  }
`;

const NavBar = () => {
  return (
    <NavBarContainer>
      <NavButton>Home</NavButton>
      <NavButton>About</NavButton>
      <NavButton>Contact</NavButton>
      <NavButton>Help</NavButton>
    </NavBarContainer>
  );
};

export default NavBar;
