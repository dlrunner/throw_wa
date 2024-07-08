document.getElementById('allButton').addEventListener('click', function() {
  const button = document.getElementById('allButton');
  const resultDiv = document.getElementById('result');
  button.disabled = true;
  resultDiv.textContent = '처리 중...';

  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    let url = tabs[0].url;

    fetch('http://localhost:8080/api/url', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({url: url}),
    })
    .then(response => {
      if (!response.ok) {
        return response.text().then(text => {
          console.error('응답 텍스트:', text); // 응답이 HTML인지 확인하기 위해 텍스트 출력
          throw new Error('API 호출 실패: ' + response.status + ', ' + text);
        });
      }
      return response.json();
    })
    .then(data => {
      if (data.success) {
        resultDiv.textContent = '북마크에 저장되었습니다.';
      } else {
        throw new Error(data.message || '처리 실패');
      }
    })
    .catch(error => {
      console.error('오류 발생:', error);
      resultDiv.textContent = '오류 발생: ' + error.message;
    })
    .finally(() => {
      button.disabled = false;
    });
  });
});
