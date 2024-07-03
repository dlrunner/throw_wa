// 사이드 패널 온/오프
chrome.action.onClicked.addListener((tab) => {
  chrome.sidePanel.setPanelBehavior({openPanelOnActionClick: true});
  chrome.sidePanel.open();
});

chrome.runtime.onInstalled.addListener(() => {
  console.log('Extension installed');
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'getUser') {
    chrome.storage.sync.get(['username', 'password'], function(data) {
      sendResponse({ username: data.username, password: data.password });
    });
    return true; // Indicates that the response is asynchronous
  }
});