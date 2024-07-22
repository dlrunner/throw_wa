import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../Components/OnBoarding.css';

const Onboarding = () => {
    const navigate = useNavigate();
  
    const handleLogoClick = () => {

      document.querySelector('.logo').classList.add('wave-effect');
  
      setTimeout(() => {
        navigate('/home');
      }, 1000); 
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