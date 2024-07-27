import requests

url = "http://ec2-3-36-89-153.ap-northeast-2.compute.amazonaws.com:8000/api/pdf_text"
data = {
    "url": "http://http-server:8000/The%20Science%20of%20Detecting%20LLM%20Generated%20Texts.pdf",
    "type": "PDF",
    "date": "2023-01-01",
    "userId": "user123",
    "userName": "John Doe"
}

try:
    response = requests.post(url, json=data)
    response.raise_for_status()  # HTTPError 발생 시 예외 처리
    print(response.json())
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
