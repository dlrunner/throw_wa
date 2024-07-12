// BottomBox.js

import React from 'react';
import './BottomBox.css';

const BottomBox = () => {
  const handleClick = (buttonNumber) => {
    alert(`Button ${buttonNumber} clicked!`);
  };

  return (
    <div className="bottom-box">
      <button onClick={() => handleClick(1)} className="bottom-button">Button 1</button>
      <button onClick={() => handleClick(2)} className="bottom-button">Button 2</button>
      <button onClick={() => handleClick(3)} className="bottom-button">Button 3</button>
    </div>
  );
};

export default BottomBox;
