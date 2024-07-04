document.addEventListener('DOMContentLoaded', function() {
  const loginContainer = document.getElementById('login-container');
  const logoutContainer = document.getElementById('logout-container');
  const loginForm = document.getElementById('login-form');
  const loginButton = document.getElementById('login-button');
  const logoutButton = document.getElementById('logout-button');
  const scrapButton = document.getElementById('scrap-button');
  const captureButton = document.getElementById('capture-button');
  const linkButton = document.getElementById('link-button');

  // 로그인 상태 확인 및 자동 로그인
  chrome.storage.sync.get(['token'], function(data) {
    if (data.token) {
      // 토큰 유효성 검사를 통해 자동 로그인 확인
      fetch('https://your-backend.com/api/auth/verify-token', {
        headers: {
          'Authorization': `Bearer ${data.token}`
        }
      })
      .then(response => response.json())
      .then(data => {
        if (data.valid) {
          showLogoutContainer();
        } else {
          showLoginContainer();
        }
      })
      .catch(() => {
        showLoginContainer();
      });
    } else {
      showLoginContainer();
    }
  });

  loginForm.addEventListener('submit', function(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch('https://your-backend.com/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
      if (data.token) {
        chrome.storage.sync.set({ token: data.token }, function() {
          document.getElementById('message').innerText = 'Login successful!';
          showLogoutContainer();
        });
      } else {
        document.getElementById('message').innerText = 'Login failed!';
      }
    })
    .catch(error => {
      document.getElementById('message').innerText = 'Login failed!';
      console.error('Error:', error);
    });
  });

  loginButton.addEventListener('click', function() {
    chrome.identity.getAuthToken({ interactive: true }, function(token) {
      if (chrome.runtime.lastError || !token) {
        document.getElementById('message2').innerText = 'Failed to get token';
        return;
      }
      fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      .then(response => response.json())
      .then(data => {
        document.getElementById('message2').innerText = `Hello, ${data.name}`;
        // Send user info to the backend
        fetch('https://your-backend.com/api/auth/google', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ token })
        })
        .then(response => response.json())
        .then(data => {
          if (data.token) {
            chrome.storage.sync.set({ token: data.token }, function() {
              showLogoutContainer();
            });
          } else {
            document.getElementById('message2').innerText = 'Google login failed!';
          }
        })
        .catch(error => {
          console.error('Error sending user info to the backend:', error);
        });
      })
      .catch(error => {
        console.error('Error fetching user info:', error);
      });
    });
  });

  logoutButton.addEventListener('click', function() {
    chrome.storage.sync.remove(['token'], function() {
      document.getElementById('message').innerText = 'Logged out';
      showLoginContainer();
    });
  });

  scrapButton.addEventListener('click', function() {
    alert('Scrap button clicked');
  });

  captureButton.addEventListener('click', function() {
    alert('Capture button clicked');
  });

  linkButton.addEventListener('click', function() {
    alert('Link button clicked');
  });

  function showLoginContainer() {
    loginContainer.style.display = 'block';
    logoutContainer.style.display = 'none';
  }

  function showLogoutContainer() {
    loginContainer.style.display = 'none';
    logoutContainer.style.display = 'block';
  }
});
