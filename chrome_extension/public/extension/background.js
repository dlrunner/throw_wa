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

      // 크롤링 API 호출
      fetch(`http://ec2-3-36-89-153.ap-northeast-2.compute.amazonaws.com:8080/api/url`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url }),
      })
        .then(response => {
          console.log("API response: ", response);
          if (!response.ok) {
            return response.text().then(text => {
              throw new Error('오류 발생: ' + text);
            });
          }
          return response.json();
        })
        .then(data => {
          console.log("API data: ", data);
          if (data.success) {
            console.log('throw-wa에 저장되었습니다!');
            chrome.tabs.sendMessage(tab.id, { message: 'throw-wa에 저장되었습니다!' });
          } else {
            throw new Error(data.message || '처리 실패');
          }
        })
        .catch(error => {
          console.error('오류 발생: ' + error.message);
          chrome.tabs.sendMessage(tab.id, { message: '오류 발생: ' + error.message });
        });
    } else {
      console.error('탭 URL을 가져올 수 없습니다.');
      alert('탭 URL을 가져올 수 없습니다.');
    }
  }
});