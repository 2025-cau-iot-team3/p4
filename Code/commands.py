# commands.py

import time
import re
import threading
import requests
from datetime import datetime

from config import CITY, CITY_KO, OPENWEATHER_API_KEY
from tts_utils import speak


def get_weather_by_city(city_code: str) -> str:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_code,
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
            f"오늘 {CITY_KO}의 날씨는 {desc}이며, "
            f"기온은 {temp:.1f}도, 체감 온도는 {feels_like:.1f}도이고, "
            f"습도는 {humidity}%입니다."
        )

    except Exception:
        return "날씨 정보를 가져오는 중 오류가 발생했습니다."


def get_current_time() -> str:
    now = datetime.now()
    hour = now.hour
    minute = now.minute

    if hour >= 12:
        meridiem = "오후"
        display_hour = hour - 12 if hour > 12 else hour
    else:
        meridiem = "오전"
        display_hour = hour if hour != 0 else 12

    return f"현재 시간은 {meridiem} {display_hour}시 {minute}분입니다."


def start_timer(seconds: int):
    def _worker():
        time.sleep(seconds)
        # 필요하면 여기에서 딩 소리나 음성 알림 추가 가능
        print("[타이머] 종료!")

    threading.Thread(target=_worker, daemon=True).start()


def handle_timer_command(text: str) -> bool:
    """
    문장 안에서 '타이머' + 숫자 찾아서 타이머 설정.
    """
    if "타이머" not in text and "타이머" not in text.replace(" ", ""):
        return False

    minutes = 0
    seconds = 0

    m = re.search(r'(\d+)\s*분', text)
    if m:
        minutes = int(m.group(1))

    s = re.search(r'(\d+)\s*초', text)
    if s:
        seconds = int(s.group(1))

    if minutes == 0 and seconds == 0:
        any_num = re.search(r'(\d+)', text)
        if any_num:
            minutes = int(any_num.group(1))

    total_seconds = minutes * 60 + seconds
    if total_seconds <= 0:
        return True

    start_timer(total_seconds)

    if minutes > 0 and seconds > 0:
        speak(f"{minutes}분 {seconds}초 뒤로 타이머를 설정했습니다.")
    elif minutes > 0:
        speak(f"{minutes}분 뒤로 타이머를 설정했습니다.")
    else:
        speak(f"{seconds}초 뒤로 타이머를 설정했습니다.")

    return True
