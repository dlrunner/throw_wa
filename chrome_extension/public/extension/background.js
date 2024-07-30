chrome.action.onClicked.addListener((tab) => {
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
  chrome.sidePanel.open();
});

chrome.runtime.onInstalled.addListener(() => {
  console.log('Extension installed');
  // Context menu 추가
  chrome.contextMenus.create({
    id: 'crawlPage',
    title: '링크 throw-wa',
    contexts: ['page']
  });
});

// Context menu 클릭 시 크롤링 API 호출
chrome.contextMenus.onClicked.addListener((info, tab) => {
  console.log("Context menu clicked", info, tab);
  if (info.menuItemId === 'crawlPage') {
    if (tab && tab.url) {
      const url = tab.url;
      console.log("Tab URL: ", url);

      const getTokenLocal = (callback) => {
        chrome.storage.local.get(['jwtToken'], (result) => {
          if (result.jwtToken) {
            callback(result.jwtToken);
          } else {
            console.error('No token found');
            callback(null);
          }
        });
      };

      getTokenLocal(async (token) => {
        if (token) {
          console.log('Token retrieved:', token);
          try {
            const response = await fetch(`http://ec2-3-35-174-211.ap-northeast-2.compute.amazonaws.com:8080/api/url`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ url: url, token: token }),
            });

            if (!response.ok) {
              const text = await response.text();
              throw new Error('오류 발생: ' + text);
            }

            const data = await response.json();
            console.log("API data: ", data);

            if (data.success) {
              console.log('throw-wa에 저장되었습니다!');
              chrome.tabs.sendMessage(tab.id, { message: 'throw-wa에 저장되었습니다!' });
            } else {
              throw new Error(data.message || '처리 실패');
            }
          } catch (error) {
            console.error('오류 발생: ' + error.message);
            chrome.tabs.sendMessage(tab.id, { message: '오류 발생: ' + error.message });
          }
        } else {
          console.error('토큰을 가져올 수 없습니다.');
          chrome.tabs.sendMessage(tab.id, { message: '토큰을 가져올 수 없습니다.' });
        }
      });
    } else {
      console.error('탭 URL을 가져올 수 없습니다.');
      alert('탭 URL을 가져올 수 없습니다.');
    }
  }
});
