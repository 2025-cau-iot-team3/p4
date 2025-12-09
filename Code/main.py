# main.py

from config import CITY
from audio_stt import load_cmd_model, transcribe_audio_from_array
from audio_stream import start_stream, get_next_utterance
from commands import handle_timer_command, get_weather_by_city, get_current_time
from tts_utils import speak, play_ding
from wakeword import is_wake_word


def main():
    cmd_model = load_cmd_model()
    stream = start_stream()

    print("=== 인공지능 비서 모모 ===")
    print("프로그램 종료: Ctrl + C\n")

    mode = "sleep"

    try:
        while True:
            # 1) 말 한 문장 들어오기
            audio_data = get_next_utterance()
            text = transcribe_audio_from_array(cmd_model, audio_data)

            # STT가 text를 못 만들었으면 무시
            if not text:
                continue

            print(f"[STT] {text}")
            # ---------------------------------
            # (1) WAITING — 웨이크워드 감지
            # ---------------------------------
            if mode == "sleep":
                if is_wake_word(text):
                    play_ding() 
                    mode = "wait_cmd"
                continue

            # ---------------------------------
            # (2) 명령 대기 상태
            # ---------------------------------
            if mode == "wait_cmd":
                handled = False

                # 타이머
                if handle_timer_command(text):
                    handled = True

                # 날씨
                if "날씨" in text:
                    speak(get_weather_by_city(CITY))
                    handled = True

                # 현재 시간
                if ("시간" in text) or ("몇 시" in text) or ("몇시" in text.replace(" ", "")):
                    speak(get_current_time())
                    handled = True

                # 처리 후 다시 sleep
                mode = "sleep"
                continue

    except KeyboardInterrupt:
        print("\n[시스템] 종료합니다.")
    finally:
        try:
            stream.stop()
            stream.close()
        except:
            pass


if __name__ == "__main__":
    main()
