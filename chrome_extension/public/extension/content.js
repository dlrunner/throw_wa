console.log("content script가 오는지 확인");

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("Message received in content script: ", request);
  if (request.message) {
    alert(request.message);
    sendResponse({ status: "Message received" });
  }
});
