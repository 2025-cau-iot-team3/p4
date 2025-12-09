# 🎤 모모 음성 비서 (Raspberry Pi + Vosk + gTTS)

라즈베리파이에서 동작하는 초간단 음성 비서 프로젝트입니다.  
사용자가 말한 문장 속에 `날씨` / `시간(시각)` / `타이머` 가 포함되어 있으면  
해당 기능을 실행하고 TTS(음성)로 읽어줍니다.

✅ 웨이크워드 필요 없음  
✅ 완전 로컬 STT (Vosk)  
✅ 날씨/시간/타이머만 음성 출력  
✅ 그 외 문장은 터미널 출력만 수행  

---

## 1. 라즈베리파이 최초 준비

Raspberry Pi OS 설치 후 SD카드를 삽입하여 부팅합니다.  
와이파이를 연결한 뒤 SSH를 활성화합니다.

```bash
sudo raspi-config
```

Interface Options → SSH → Enable

시스템 업데이트:

```bash
sudo apt update
sudo apt upgrade -y
```

필수 패키지 설치:

```bash
sudo apt install -y python3 python3-pip python3-venv ffmpeg alsa-utils git
```

---

## 2. GitHub 프로젝트 받기

```bash
cd ~
git clone https://github.com/사용자명/저장소명.git
cd 저장소명/pi4/Code
```

---

## 3. 가상환경 생성 및 활성화

```bash
python3 -m venv ~/venv
source ~/venv/bin/activate
```

---

## 4. 파이썬 라이브러리 설치

```bash
pip install --upgrade pip
pip install sounddevice scipy numpy gTTS requests vosk
```

---

## 5. Vosk 한국어 모델 설치

모델 다운로드:
https://alphacephei.com/vosk/models  

모델명:
```text
vosk-model-small-ko-0.22
```

모델 위치:
```text
/home/사용자/models/vosk-model-small-ko-0.22/
```

simple_assistant_whisper.py 내부 모델 경로:
```python
VOSK_MODEL_PATH = "/home/사용자/models/vosk-model-small-ko-0.22"
```

---

## 6. 오디오 장치 테스트

장치 확인:
```bash
arecord -l
aplay -l
```

마이크 녹음 테스트:
```bash
arecord -D plughw:2,0 -f S16_LE -c 1 -r 16000 -d 3 test.wav
aplay test.wav
```

스피커 테스트:
```bash
speaker-test -t wav
```

---

## 7. config.py 설정

```python
OPENWEATHER_API_KEY = "여기에_본인_API_키"
CITY = "Seoul,KR"
CITY_KO = "서울"
DEVICE = "cpu"
CMD_MODEL_NAME = "tiny"
```

OpenWeather API 키 발급:
https://openweathermap.org/api

---

## 8. 실행 방법

```bash
ssh 사용자@raspberrypi.local
source ~/venv/bin/activate
cd ~/pi4/Code
python3 simple_assistant_whisper.py
```

---

## 9. 사용 방법

프로그램 실행 시 다음 문구가 출력됩니다.

```text
원하시는 기능을 말해주세요.
예: 오늘 날씨 알려줘 / 지금 시간 알려줘 / 3분 타이머 맞춰줘
5초 안에 말씀하지 않으면 준비를 종료합니다.
```

날씨, 시간, 타이머가 포함된 문장만 TTS로 출력됩니다.

---

## 10. 종료 방법

```bash
Ctrl + C
deactivate
exit
```

---

## 11. 파일 구조

```text
pi4/Code/
├── simple_assistant_whisper.py
├── config.py
```

---

## 12. 문제 발생 시 확인

```bash
which ffmpeg
which aplay
speaker-test -t wav
ls /home/s사용자/models/vosk-model-small-ko-0.22
```

---

## 13. 사용 기술

STT: Vosk  
TTS: gTTS  
Audio: ALSA, ffmpeg  
Weather API: OpenWeatherMap  

---

## 14. 라이선스

본 프로젝트는 학습 및 개인 프로젝트 용도입니다.
