import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import whisper
import threading
import msvcrt
import warnings

# 경고 숨기기
warnings.filterwarnings("ignore")

SAMPLE_RATE = 16000
recording = []
is_recording = True

def record_audio():
    global recording, is_recording
    def callback(indata, frames, time, status):
        if is_recording:
            recording.append(indata.copy())
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=callback):
        while is_recording:
            sd.sleep(100)

def transcribe_audio(model):
    if not recording:
        return
    audio_data = np.concatenate(recording, axis=0)
    wav_path = "mic_auto.wav"
    write(wav_path, SAMPLE_RATE, (audio_data * 32767).astype(np.int16))
    result = model.transcribe(wav_path, language="ko")
    print("인식 결과:", result["text"])

def wait_key():
    while True:
        ch = msvcrt.getch()
        if ch == b' ':
            return "space"
        if ch == b'\r':
            return "enter"

def main():
    global recording, is_recording
    model = whisper.load_model("base")  # GPU 없으면 자동으로 CPU로 실행

    while True:
        recording.clear()
        is_recording = True
        print("\n 녹음해주세요 (스페이스: 종료 / 엔터: 프로그램 종료)")
        thread = threading.Thread(target=record_audio)
        thread.start()

        key = wait_key()
        is_recording = False
        thread.join()

        if key == "space":
            transcribe_audio(model)
        elif key == "enter":
            print("프로그램을 종료.")
            break

if __name__ == "__main__":
    main()
