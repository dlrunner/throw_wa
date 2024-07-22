import React from 'react';
import './BookLoader.css'; // 여기서 CSS 파일을 임포트 합니다.

const BookLoader = () => {
  return (
    <div className="book-loader">
      <div className="book">
        <div className="cover"></div>
        <div className="page"></div>
        <div className="back"></div>
      </div>
    </div>
  );
};

export default BookLoader;