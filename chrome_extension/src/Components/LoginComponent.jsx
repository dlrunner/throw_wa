import React from 'react';
import { GoogleLogin } from 'react-google-login';
import KakaoLogin from 'react-kakao-login';

const LoginComponent = () => {
    const handleGoogleSuccess = (response) => {
        console.log(response);
    };

    const handleGoogleFailure = (response) => {
        console.log(response);
    };

    const handleKakaoSuccess = (response) => {
        console.log(response);
    };

    const handleKakaoFailure = (response) => {
        console.log(response);
    };

    return (
        <div className="login-container">
            <h2>Login</h2>
            <div className="input-container">
                <label htmlFor="email">Email</label>
                <input type="email" id="email" name="email" />
            </div>
            <div className="input-container">
                <label htmlFor="password">Password</label>
                <input type="password" id="password" name="password" />
            </div>
            <div className="social-login-buttons">
                <GoogleLogin
                    clientId="YOUR_GOOGLE_CLIENT_ID"
                    buttonText="Login with Google"
                    onSuccess={handleGoogleSuccess}
                    onFailure={handleGoogleFailure}
                    cookiePolicy={'single_host_origin'}
                />
                <KakaoLogin
                    jsKey="YOUR_KAKAO_JS_KEY"
                    buttonText="Login with Kakao"
                    onSuccess={handleKakaoSuccess}
                    onFailure={handleKakaoFailure}
                    getProfile={true}
                />
            </div>
        </div>
    );
};

export default LoginComponent;
