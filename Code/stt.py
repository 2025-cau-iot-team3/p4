import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import whisper
import threading
import msvcrt
import warnings
import requests   # 날씨 API 호출용
from datetime import datetime  # 현재 시간 얻기용

# 경고 숨기기
warnings.filterwarnings("ignore")

SAMPLE_RATE = 16000
recording = []
is_recording = True


OPENWEATHER_API_KEY = "YOUR_WEATHER_API_CODE" # <- 이 부분은 본인의 OpenWeather API 코드를 입력해야함.
CITY = "Seoul,KR"  # 원하는 지역으로 변경


def get_weather_by_city(city: str) -> str:
    """
    OpenWeatherMap에서 현재 날씨를 가져와서
    사람이 읽기 좋은 한글 문자열로 반환
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "kr",
    }

    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        desc = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]

        return (
            f"[현재 날씨 정보]\n"
            f"도시: {city}\n"
            f"기온: {temp:.1f}°C (체감 {feels_like:.1f}°C)\n"
            f"습도: {humidity}%\n"
            f"상태: {desc}"
        )

    except Exception as e:
        return f"날씨 정보를 가져오는 중 오류 발생: {e}"


def get_current_time() -> str:
    """
    현재 컴퓨터 기준 시간을 한국어 문장으로 반환
    """
    now = datetime.now()
    hour = now.hour
    minute = now.minute

    # 오전 / 오후 변환
    if hour >= 12:
        meridiem = "오후"
        display_hour = hour - 12 if hour > 12 else hour
    else:
        meridiem = "오전"
        display_hour = hour if hour != 0 else 12  # 0시는 12시로 표시

    return f"현재 시간은 {meridiem} {display_hour}시 {minute}분입니다."


def record_audio():
    global recording, is_recording
    def callback(indata, frames, time, status):
        if is_recording:
            recording.append(indata.copy())
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=callback):
        while is_recording:
            sd.sleep(100)


def transcribe_audio(model):
    global recording
    if not recording:
        return ""

    audio_data = np.concatenate(recording, axis=0)
    wav_path = "mic_auto.wav"
    write(wav_path, SAMPLE_RATE, (audio_data * 32767).astype(np.int16))

    result = model.transcribe(
        wav_path,
        language="ko",
        fp16=False,
        temperature=0.0,
        condition_on_previous_text=False
    )

    text = result["text"].strip()
    print("인식 결과:", text)
    return text


def wait_key():
    while True:
        ch = msvcrt.getch()
        if ch == b' ':
            return "space"
        if ch == b'\r':
            return "enter"


def main():
    global recording, is_recording
    model = whisper.load_model("small")

    while True:
        # 새 녹음 시작
        recording = []
        is_recording = True
        print("\n녹음해주세요 (스페이스: 이 녹음 종료 / 엔터: 프로그램 종료)")

        thread = threading.Thread(target=record_audio)
        thread.start()

        # 녹음에 대한 키 입력
        key = wait_key()
        is_recording = False
        thread.join()

        if key == "enter":
            print("프로그램을 종료.")
            break

        # Whisper 음성 인식
        text = transcribe_audio(model)

        # 아무 것도 인식 못했으면 패스
        if not text:
            print("아무 내용도 인식되지 않았습니다.")
        else:
            # "날씨" 키워드 포함되어 있으면 자동으로 날씨 알려줌
            if "날씨" in text:
                print("\n'날씨' 키워드를 감지했습니다. 날씨 정보를 불러옵니다...\n")
                print(get_weather_by_city(CITY))
                print()

            # "시간" 관련 키워드 포함되면 현재 시간 알려줌
            if ("시간" in text) or ("몇 시" in text) or ("몇시" in text):
                print("\n'시간' 키워드를 감지했습니다. 현재 시각을 알려드립니다...\n")
                print(get_current_time())
                print()

        # 다시 할지 말지 선택
        print("다시 녹음하려면 스페이스, 종료하려면 엔터를 눌러주세요.")
        key2 = wait_key()

        if key2 == "enter":
            print("프로그램을 종료.")
            break


if __name__ == "__main__":
    main()
