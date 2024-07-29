import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../Components/OnBoarding.css';

const Onboarding = () => {
  const navigate = useNavigate();

  const handleLogoClick = () => {

    document.querySelector('.logo').classList.add('wave-effect');

    getTokenLocal(async function (token) {
      if (token) {
        console.log('Token retrieved:', token);
        setTimeout(() => {
          navigate('/home');
        }, 1000);
      } else {
        setTimeout(() => {
          navigate('/login');
        }, 1000);
      }
    })
  };

  const getTokenLocal = (callback) => {
    if (typeof localStorage !== 'undefined') {
      const token = localStorage.getItem('jwtToken');
      callback(token);
    } else {
      console.error('localStorage is not available');
    }
  };

  return (
    <div className="onboarding-container">
      <img
        src="/logo/logo.png"
        alt="Logo"
        className="logo"
        onClick={handleLogoClick}
      />
    </div>
  );
};

export default Onboarding;