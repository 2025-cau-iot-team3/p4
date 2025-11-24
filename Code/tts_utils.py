# tts_utils.py

import os
import sys
import threading
import tempfile
from gtts import gTTS

# 로봇이 말하는 중인지 표시 (말하는 동안에는 마이크 입력 무시)
is_speaking = threading.Event()


def speak_block(text: str):
    """
    실제 TTS 작업 (블로킹) - 쓰레드에서 실행됨.
    """
    print("[로봇]", text)
    is_speaking.set()

    try:
        if sys.platform.startswith("win"):
            base_dir = r"C:\tts_tmp"
        else:
            base_dir = "/tmp/tts_tmp"

        os.makedirs(base_dir, exist_ok=True)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", dir=base_dir) as tf:
            tts_path = tf.name

        tts = gTTS(text=text, lang='ko')
        tts.save(tts_path)

        if sys.platform.startswith("win"):
            from playsound import playsound
            playsound(tts_path)
        else:
            os.system(f"mpg123 -q '{tts_path}'")

        try:
            os.remove(tts_path)
        except Exception:
            pass

    except Exception as e:
        print(f"[TTS 에러] {e}")
    finally:
        is_speaking.clear()


def speak(text: str):
    """
    메인 루프를 막지 않고 TTS 실행.
    """
    threading.Thread(target=speak_block, args=(text,), daemon=True).start()


def play_ding():
    """
    같은 폴더에 ding.wav 파일 두고 사용.
    """
    ding_path = os.path.join(os.path.dirname(__file__), "ding.wav")

    if sys.platform.startswith("win"):
        import winsound
        winsound.PlaySound(ding_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    else:
        os.system(f"aplay '{ding_path}' >/dev/null 2>&1 &")
