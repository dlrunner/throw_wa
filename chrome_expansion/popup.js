document.getElementById('transcribeButton').addEventListener('click', function() {
  // 버튼 비활성화 및 로딩 메시지 표시
  const button = document.getElementById('transcribeButton');
  const resultDiv = document.getElementById('result');
  button.disabled = true;
  resultDiv.textContent = '변환 중...';

  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    let url = tabs[0].url;

    // 유튜브 동영상 전사 API 호출
    fetch('http://localhost:8000/api/youtube_text', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({url: url, language: 'ko'}),
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('유튜브 영상이 없습니다.');
      }
      return response.json();
    })
    .then(data => {
      if (data.success) {
        resultDiv.textContent = '북마크에 저장 되었습니다.';
      } else {
        throw new Error(data.detail || '유튜브 동영상 전사 실패');
      }
    })
    .catch(error => {
      console.error('오류 발생:', error);
      resultDiv.textContent = '오류 발생: ' + error.message;
    })
    .finally(() => {
      // 작업 완료 후 버튼 다시 활성화
      button.disabled = false;
    });
  });
});

document.getElementById('pdfButton').addEventListener('click', function() {
  // 버튼 비활성화 및 로딩 메시지 표시
  const button = document.getElementById('pdfButton');
  const resultDiv = document.getElementById('result');
  button.disabled = true;
  resultDiv.textContent = '추출 중...';

  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    let url = tabs[0].url;

    // PDF 링크 텍스트 추출 API 호출
    fetch('http://localhost:8000/api/pdf_text', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({url: url}),
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('PDF 링크 텍스트 추출 API 호출 실패: ' + response.status);
      }
      return response.json();
    })
    .then(data => {
      if (data.success) {
        resultDiv.textContent = '북마크에 저장 되었습니다.';
      } else {
        throw new Error(data.detail || 'PDF 링크 텍스트 추출 실패');
      }
    })
    .catch(error => {
      console.error('오류 발생:', error);
      resultDiv.textContent = '오류 발생:' + error.message;
    })
    .finally(() =>{
      button.disabled = false
    })
  })
})

document.getElementById('crawlingButton').addEventListener('click', function() {
  // 버튼 비활성화 및 로딩 메시지 표시
  const button = document.getElementById('crawlingButton');
  const resultDiv = document.getElementById('result');
  button.disabled = true;
  resultDiv.textContent = '추출 중...';

  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    let url = tabs[0].url;

    // PDF 링크 텍스트 추출 API 호출
    fetch('http://localhost:8000/api/crawler', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({url: url}),
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('크롤링 API 호출 실패: ' + response.status);
      }
      return response.json();
    })
    .then(data => {
      if (data.success) {
        resultDiv.textContent = '북마크에 저장 되었습니다.';
      } else {
        throw new Error(data.detail || '크롤링 텍스트 추출 실패');
      }
    })
    .catch(error => {
      console.error('오류 발생:', error);
      resultDiv.textContent = '오류 발생:' + error.message;
    })
    .finally(() =>{
      button.disabled = false
    })
  })
})