# commands.py

import time
import re
import threading
import requests
from datetime import datetime

from config import CITY, CITY_KO, OPENWEATHER_API_KEY
from tts_utils import speak


def get_weather_by_city(city_code: str) -> str:
    """
    OpenWeather API를 이용해 현재 날씨 정보를 가져와서
    한국어로 읽기 좋은 문장으로 반환.
    """
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
    """
    현재 시간을 한국어로 읽기 좋은 형식으로 반환.
    예) '현재 시간은 오후 3시 25분입니다.'
    """
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


def start_timer(seconds: int, announce_text: str = None, done_text: str = None):
    """
    타이머 전용 스레드.
    1) 안내 멘트(TTS)를 먼저 끝까지 재생하고
    2) 그 다음에 seconds 만큼 대기한 뒤
    3) 종료 멘트/로그를 출력.

    이렇게 하면 '10초 타이머'라고 했을 때,
    TTS 말이 다 끝난 후부터 10초를 재기 때문에
    실제 체감 시간이 정확해짐.
    """

    def _worker():
        # 1) 타이머 설정 안내 멘트 먼저 말하기
        if announce_text:
            speak(announce_text)

        # 2) 안내 멘트가 끝난 뒤부터 카운트다운 시작
        time.sleep(seconds)

        # 3) 타이머 종료 알림
        print("[타이머] 종료!")
        if done_text:
            speak(done_text)

    threading.Thread(target=_worker, daemon=True).start()


def handle_timer_command(text: str) -> bool:
    """
    문장 안에서 '타이머' + 숫자(분/초)를 찾아서 타이머 설정.

    예)
      - "10초 타이머 해줘"
      - "3분 타이머"
      - "1분 30초 뒤에 알려줘"

    동작 방식:
    - '타이머'라는 단어가 없으면 False 반환 (이 명령이 아님)
    - 분/초를 파싱해서 total_seconds 계산
    - TTS로 '몇 분 몇 초 뒤 타이머 설정' 안내 멘트를 먼저 말하고,
      그 다음부터 실제 카운트다운을 시작.
    """
    # '타이머'라는 단어가 아예 없으면 이 핸들러가 처리하지 않음
    if "타이머" not in text and "타이머" not in text.replace(" ", ""):
        return False

    minutes = 0
    seconds = 0

    # "3분", "10분" 등 찾기
    m = re.search(r'(\d+)\s*분', text)
    if m:
        minutes = int(m.group(1))

    # "5초", "30초" 등 찾기
    s = re.search(r'(\d+)\s*초', text)
    if s:
        seconds = int(s.group(1))

    # '분' '초'가 둘 다 없고 그냥 숫자만 있는 경우 → 분으로 처리
    # 예: "타이머 3개", "타이머 10" 같은 건 3분, 10분으로 가정
    if minutes == 0 and seconds == 0:
        any_num = re.search(r'(\d+)', text)
        if any_num:
            minutes = int(any_num.group(1))

    total_seconds = minutes * 60 + seconds
    if total_seconds <= 0:
        # 숫자는 있지만 0초 이하인 이상한 경우 → 그냥 처리했다고만 보고 종료
        return True

    # 안내 멘트용 문장 구성
    if minutes > 0 and seconds > 0:
        announce = f"{minutes}분 {seconds}초 뒤로 타이머를 설정했습니다."
    elif minutes > 0:
        announce = f"{minutes}분 뒤로 타이머를 설정했습니다."
    else:
        announce = f"{seconds}초 뒤로 타이머를 설정했습니다."

    # 타이머 종료 멘트
    done_text = "타이머가 종료되었습니다."

    # ✅ TTS 안내를 먼저 말하고,
    #    그 이후에 total_seconds만큼 기다리도록 타이머 스레드에서 처리
    start_timer(total_seconds, announce_text=announce, done_text=done_text)

    return True
