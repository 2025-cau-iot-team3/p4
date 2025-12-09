#수정본

import os
import re
import time
import subprocess
import wave
import json
from datetime import datetime

import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from gtts import gTTS
import requests
from vosk import Model, KaldiRecognizer

from config import (
    OPENWEATHER_API_KEY,
    CITY,
    CITY_KO,
)

# ==============================
# 1. Vosk 한국어 모델 로딩
# ==============================

VOSK_MODEL_PATH = "/home/soargrape/models/vosk-model-small-ko-0.22"

print("[시스템] Vosk 한국어 모델 로딩 중...")
vosk_model = Model(VOSK_MODEL_PATH)
print("[시스템] Vosk 한국어 모델 로딩 완료.")


# ==============================
# 2. TTS (gTTS → ffmpeg → aplay)
#    👉 날씨 / 시간 / 타이머에서만 사용
# ==============================

def speak_korean(text: str):
    """
    gTTS로 한국어 음성을 생성하고,
    ffmpeg으로 WAV로 변환 후 aplay로 재생.
    (날씨 / 시간 / 타이머 응답에서만 호출)
    """
    if not text:
        return

    print(f"[TTS 출력] {text}")

    mp3_path = "tts_output.mp3"
    wav_path = "tts_output.wav"

    # 1) gTTS로 MP3 생성
    try:
        tts = gTTS(text=text, lang="ko")
        tts.save(mp3_path)
    except Exception as e:
        print("[TTS] gTTS 오류:", e)
        return

    # 2) ffmpeg으로 WAV(16kHz, 모노) 변환
    try:
        cmd = [
            "ffmpeg",
            "-y",
            "-loglevel", "quiet",
            "-i", mp3_path,
            "-ac", "1",
            "-ar", "16000",
            wav_path,
        ]
        subprocess.run(cmd, check=False)
    except Exception as e:
        print("[TTS] ffmpeg 변환 오류:", e)
        return

    # 3) aplay로 WAV 재생 (기본 스피커)
    try:
        subprocess.run(["aplay", "-q", wav_path])
    except Exception as e:
        print("[TTS] aplay 재생 오류:", e)


# ==============================
# 3. 오디오 녹음 (5초, 16kHz 고정)
# ==============================

SAMPLE_RATE = 16000  # STT용 샘플레이트 고정


def record_once(seconds: int = 5, filename: str = "simple_input.wav") -> tuple[str, int]:
    """
    sounddevice로 'seconds' 만큼 녹음 후 WAV 파일로 저장
    """
    samplerate = SAMPLE_RATE
    print(f"[녹음] {seconds}초 동안 녹음합니다. 말씀하세요...")
    print(f"[시스템] 입력 샘플레이트: {samplerate}")

    recording = sd.rec(
        int(seconds * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype="float32",
    )
    sd.wait()
    print("[녹음] 종료")

    # float32 -> int16 변환 후 저장
    audio_int16 = np.int16(recording * 32767)
    write(filename, samplerate, audio_int16)

    return filename, samplerate


# ==============================
# 4. Vosk로 STT
# ==============================

def stt_vosk(filepath: str, samplerate: int) -> str:
    """
    Vosk 로컬 모델로 한국어 음성 인식
    (짧은 문장용, 파일 전체를 한 번에 처리)
    """
    try:
        wf = wave.open(filepath, "rb")

        if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
            print("[STT] WAV 포맷이 다릅니다. 16-bit 모노를 권장합니다.")
        print(f"[STT] Vosk에 전송: {filepath}, fr={wf.getframerate()}, len={os.path.getsize(filepath)} bytes")

        rec = KaldiRecognizer(vosk_model, wf.getframerate())
        text_result = ""

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                pass

        final = rec.FinalResult()
        j = json.loads(final)
        text_result = (j.get("text") or "").strip()
        print("[STT 결과]", text_result)
        return text_result

    except Exception as e:
        print("[오류] Vosk STT 중 예외 발생:", e)
        return ""


# ==============================
# 5. 날씨 / 시간 / 타이머 처리
# ==============================

def get_weather_by_city(city_code: str) -> str:
    """
    OpenWeatherMap에서 현재 날씨를 가져와 한글 문장으로 반환
    예: '현재 서울 날씨는 맑음이며, 온도는 3.2도, 체감 온도는 0.5도입니다.'
    """
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city_code,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "lang": "kr",
        }
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()

        if "weather" not in data or "main" not in data:
            return "날씨 정보를 가져오는데 실패했습니다."

        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feels = data["main"]["feels_like"]

        return (
            f"현재 {CITY_KO} 날씨는 {desc}이며, "
            f"온도는 {temp:.1f}도, 체감 온도는 {feels:.1f}도입니다."
        )
    except Exception as e:
        print("[오류] 날씨 API:", e)
        return "날씨 정보를 가져오는데 오류가 발생했습니다."


def get_time_message() -> str:
    """
    현재 시간을 한국어 문장으로 반환
    """
    now = datetime.now()
    h = now.hour
    m = now.minute
    return f"현재 시간은 {h}시 {m}분입니다."


def parse_timer_minutes(text: str) -> int:
    """
    '3분', '5분 타이머', '10분만' 같은 문장에서 분 단위 숫자를 추출
    없으면 기본 3분.
    """
    m = re.search(r"(\d+)\s*분", text)
    if m:
        return int(m.group(1))
    return 3


def handle_command(text: str):
    """
    전체 문장을 받아서
    - '날씨' / '기온' / '온도'  포함 → 날씨 TTS + 출력
    - '시간' / '시각' / '몇 시' 포함 → 현재 시간 TTS + 출력
    - '타이머' / '알람' 포함 → 타이머 TTS + 출력
    그 외 안내는 콘솔에만 출력 (TTS X)
    """
    if not text:
        print("[안내] 인식된 텍스트가 없습니다.")
        return

    no_space = text.replace(" ", "")

    # 1) 날씨 관련
    if ("날씨" in no_space) or ("기온" in no_space) or ("온도" in no_space):
        msg = get_weather_by_city(CITY)
        print("[날씨 응답]", msg)
        speak_korean(msg)   # ✅ 여기서만 TTS
        return

    # 2) 시간 / 시각 관련
    if ("시간" in no_space) or ("시각" in no_space) or ("몇시" in no_space):
        msg = get_time_message()
        print("[시간 응답]", msg)
        speak_korean(msg)   # ✅ 여기서만 TTS
        return

    # 3) 타이머 / 알람 관련
    if ("타이머" in no_space) or ("알람" in no_space):
        minutes = parse_timer_minutes(no_space)
        start_msg = f"{minutes}분 뒤에 알려드릴게요."
        print("[타이머 설정]", start_msg)
        speak_korean(start_msg)   # ✅ 시작 안내도 TTS

        # 매우 단순한 블로킹 타이머
        time.sleep(minutes * 60)

        end_msg = f"{minutes}분 타이머가 종료되었습니다."
        print("[타이머 종료]", end_msg)
        speak_korean(end_msg)     # ✅ 종료 안내도 TTS
        return

    # 4) 해당 키워드가 하나도 없을 때 → 글만 출력
    print("[안내] 인식된 문장:", text)
    print("[안내] 아직은 날씨, 시간, 타이머와 관련된 말만 이해할 수 있어요.")
    # ❌ TTS 호출하지 않음


# ==============================
# 6. 메인 루프
#   - 실행 즉시 "원하시는 기능을 말해주세요"
#   - 5초 듣기
#   - 엔터로 다시 시작
# ==============================

def main():
    print("=== 모모 비서 (단일 명령 모드: 음성으로 '날씨/시간/타이머' 요청) ===\n")

    first = True

    while True:
        if first:
            # 처음 한 번은 바로 시작
            first = False
        else:
            # 이후에는 엔터로 다시 시작
            input("\n>>> 다시 명령을 시작하시려면 엔터를 눌러 주세요 : ")

        print("\n원하시는 기능을 말해주세요.")
        print("예: 오늘 날씨 알려줘 / 지금 시간 알려줘 / 3분 타이머 맞춰줘")
        print("5초 안에 말씀하지 않으면 준비를 종료합니다.\n")

        # 5초 동안 녹음
        audio_path, sr = record_once(seconds=5)
        text = stt_vosk(audio_path, sr)

        print("[STT - 전체 인식 결과]", text)

        # 아무 말도 없거나, STT가 완전 날려먹었을 때
        if not text:
            print("[안내] 5초 안에 말씀이 없어 준비를 종료합니다. 엔터로 다시 시작할 수 있습니다.")
            # ❌ 여기서는 TTS 없음
            continue  # while 처음으로 → 엔터 대기

        # 인식된 문장에 따라 명령 처리
        handle_command(text)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[시스템] 프로그램을 종료합니다.")
