#  Korean Speech-to-Text (STT) + Voice Assistant (Clover)

마이크로 말한 음성을 OpenAI Whisper로 실시간 변환하고,
웨이크워드(“모모야”) 감지 후 날씨 / 시간 / 타이머 기능을 수행하는 음성비서입니다.

스페이스바로 녹음을 종료하고 텍스트로 확인할 수 있으며,
라즈베리파이에서는 상시 음성 스트리밍 모드로 작동합니다.

---

## 설치 방법

### 필수 라이브러리 설치
아래 명령어를 **터미널(VSCode, PowerShell 등)** 에 한 줄씩 입력

```bash
pip install git+https://github.com/openai/whisper.git
pip install torch
pip install sounddevice
pip install scipy
pip install keyboard
pip install numpy
pip install requests
pip install gTTS
pip install playsound
