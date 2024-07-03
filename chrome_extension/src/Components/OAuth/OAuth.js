const Client_Id = import.meta.env.VITE_REACT_APP_CLIENT_ID;
const Redirect_Uri = import.meta.env.VITE_REACT_APP_REDIRECT_URI;

export const KAKAO_AUTH_URL = `https://kauth.kakao.com/oauth/authorize?client_id=${Client_Id}&redirect_uri=${Redirect_Uri}&response_type=code`;