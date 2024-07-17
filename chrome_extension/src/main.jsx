<<<<<<< HEAD
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { BrowserRouter, HashRouter } from 'react-router-dom'
import AppContextProvider from './contexts/AppContextProvider.jsx'

=======
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';
import { BrowserRouter, HashRouter } from 'react-router-dom';
import AppContextProvider from './contexts/AppContextProvider.jsx';
>>>>>>> 4d61793db3130c6b0a369446621bf77228caab60

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <HashRouter>
      <AppContextProvider>
        <App />
      </AppContextProvider>
    </HashRouter>
  </React.StrictMode>
);
