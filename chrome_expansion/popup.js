document.getElementById('allButton').addEventListener('click', function() {
  // 버튼 비활성화 및 로딩 메시지 표시
  const button = document.getElementById('allButton');
  const resultDiv = document.getElementById('result');
  button.disabled = true;
  resultDiv.textContent = '처리 중...';

  // 현재 활성 탭의 URL 가져오기
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    let url = tabs[0].url;

    // URL 타입 감지 함수
    function detectLinkType(url) {
      const youtubePattern = /(https?:\/\/)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)\//;
      const pdfPattern = /.*\.pdf$/;
      const imagePattern = /\.(jpeg|jpg|gif|png|bmp|tiff|webp)$/i;

      if (youtubePattern.test(url)) {
        return 'youtube';
      } else if (pdfPattern.test(url)) {
        return 'pdf';
      } else if(imagePattern.test(url)){
        return 'image';
      } else{
        return 'web';
      }
    }

    const linkType = detectLinkType(url);
    let apiEndpoint = '';

    switch (linkType) {
      case 'youtube':
        apiEndpoint = 'http://localhost:8000/api/youtube_text';
        break;
      case 'pdf':
        apiEndpoint = 'http://localhost:8000/api/pdf_text';
        break;
      case 'web':
        apiEndpoint = 'http://localhost:8000/api/crawler';
        break;
      case 'image':
        apiEndpoint ='http://localhost:8000/api/image_embedding';
        break;
      default:
        resultDiv.textContent = '지원하지 않는 링크 유형입니다.';
        button.disabled = false;
        return;
    }

    // API 호출
    fetch(apiEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({url: url}),
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('API 호출 실패: ' + response.status);
      }
      return response.json();
    })
    .then(data => {
      if (data.success) {
        resultDiv.textContent = '북마크에 저장되었습니다.';
      } else {
        throw new Error(data.detail || '텍스트 추출 실패');
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
