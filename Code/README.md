#  Korean Speech-to-Text (STT)

마이크로 말한 음성을 **OpenAI Whisper 모델**을 통해 실시간으로 텍스트로 변환하는 Python 프로그램입니다.  
스페이스바로 녹음을 종료하고 텍스트를 확인할 수 있으며, 엔터로 프로그램을 종료합니다.

---

## 설치 방법

### 필수 명령어
아래 명령어를 **터미널(VSCode, PowerShell 등)** 에 한 줄씩 입력

```bash
py -m pip install git+https://github.com/openai/whisper.git
py -m pip install torch
py -m pip install sounddevice
py -m pip install scipy
py -m pip install keyboard
