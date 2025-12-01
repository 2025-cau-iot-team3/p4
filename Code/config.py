# config.py
import torch

# 오디오 설정
SAMPLE_RATE = 16000

# OpenWeather API
OPENWEATHER_API_KEY = "YOUR_TOKEN_HERE"
CITY = "Seoul,KR"
CITY_KO = "서울"

# 디바이스 (GPU 우선 사용)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# 명령 인식용 Whisper 모델
CMD_MODEL_NAME = "tiny"   # 느리면 "base"나 "tiny"로 바꿔도 됨
