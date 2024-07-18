import React, { useState, useEffect } from 'react';
import './Character.css'; // 스타일을 정의한 CSS 파일

const Character = () => {
  const [rotation, setRotation] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (event) => {
      const { clientX, clientY } = event;
      const { innerWidth, innerHeight } = window;

      const x = (clientX / innerWidth - 0.5) * 30; // 최대 15도 회전
      const y = (clientY / innerHeight - 0.5) * 30; // 최대 15도 회전

      setRotation({ x, y });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  return (
    <div className="character-container">
      <div
        className="character"
        style={{
          transform: `rotateX(${rotation.y}deg) rotateY(${rotation.x}deg)`,
        }}
      >
        <img
          src="chrome_extension/public/logo/owl.jpg" // 이미지 파일 경로를 입력하세요
          alt="Character Logo"
          className="logo"
        />
      </div>
    </div>
  );
};

export default Character;
