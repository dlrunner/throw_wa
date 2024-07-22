import './App.css';
import { Route, Routes } from 'react-router-dom';
import Login from './Components/Login';
import Home from './Components/Home';
import Onboarding from './Components/OnBoarding';
import KakaoLoginHandler from './Components/OAuth/KakaoLoginHandler';



const App = () => {
  return (
    <div className="app">
      <Routes>
        <Route path='/' element={<Onboarding />}></Route>
        <Route path='/home' element={<Home />}></Route>
        {/* <Route path='/signup' element={<SignUp />}></Route> */}
        <Route path='/login' element={<Login />}></Route>
        <Route path='/oauth/callback/kakao' element={<KakaoLoginHandler />}></Route>
      </Routes>
    </div>
  );
};

export default App;
