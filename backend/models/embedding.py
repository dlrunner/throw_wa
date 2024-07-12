import os
import requests
from PIL import Image
from io import BytesIO
from transformers import AutoModelForCausalLM, AutoProcessor, AutoTokenizer, AutoModel
import torch
import numpy as np
from unittest.mock import patch
from transformers.dynamic_module_utils import get_imports
from fastapi import HTTPException
from googletrans import Translator

# 텍스트 임베딩 모델 설정
model_name = "intfloat/multilingual-e5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
text_model = AutoModel.from_pretrained(model_name)

# Googletrans 번역기 설정
translator = Translator()

# Florence 모델 설정
device = torch.device("cpu")

def fixed_get_imports(filename: str | os.PathLike) -> list[str]:
    imports = get_imports(filename)
    if str(filename).endswith("modeling_florence2.py") and "flash_attn" in imports:
        imports.remove("flash_attn")
    return imports

def load_florence_model():
    with patch("transformers.dynamic_module_utils.get_imports", fixed_get_imports):
        florence_model = AutoModelForCausalLM.from_pretrained("microsoft/Florence-2-base", trust_remote_code=True)
        florence_processor = AutoProcessor.from_pretrained("microsoft/Florence-2-base", trust_remote_code=True)
    florence_model.to(device)
    return florence_model, florence_processor

# Florence 모델과 프로세서를 로드
florence_model, florence_processor = load_florence_model()

# 이미지 캡셔닝 함수
def imagecaption(image_url: str):
    try:
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))

        # 이미지 캡셔닝
        prompt = "<MORE_DETAILED_CAPTION>"
        inputs = florence_processor(text=prompt, images=image, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            generated_ids = florence_model.generate(
                input_ids=inputs["input_ids"],
                pixel_values=inputs["pixel_values"],
                max_new_tokens=35,
                num_beams=3,
            )

        generated_text = florence_processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
        parsed_answer = florence_processor.post_process_generation(generated_text, task=prompt, image_size=(image.width, image.height))
        caption = parsed_answer.get("<MORE_DETAILED_CAPTION>", "No caption generated")

        return caption

    except Exception as e:
        print(f"오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 텍스트 임베딩 함수
def embed_text(text: str) -> list:
    # 텍스트를 최대 길이 77로 분할
    max_length = 77
    text_chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
    
    embeddings = []
    for chunk in text_chunks:
        inputs = tokenizer(chunk, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = text_model(**inputs)
            text_features = outputs.last_hidden_state.mean(dim=1)
        embeddings.append(text_features.squeeze().cpu().numpy())
    
    # 모든 청크 임베딩의 평균을 계산
    mean_embedding = np.mean(embeddings, axis=0)
    return mean_embedding.tolist()

# Googletrans 번역 함수
def translate_text(text: str) -> str:
    translated = translator.translate(text, dest='ko')
    return translated.text