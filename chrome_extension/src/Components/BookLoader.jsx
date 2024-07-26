import React from 'react';
import './BookLoader.css';

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