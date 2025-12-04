# audio_stream.py

import sounddevice as sd
import numpy as np
import queue
import time

from config import SAMPLE_RATE
from tts_utils import is_speaking

# 블록 / VAD 설정
INPUT_DEVICE_INDEX = 2
BLOCK_SIZE = 1024           # 약 64ms
SILENCE_THRESHOLD = 0.003   # 이 이하 RMS는 무음으로 간주
SILENCE_DURATION = 0.6      # 이 시간(초) 이상 무음이면 '말 끝남'

# 실시간 오디오 큐
audio_q = queue.Queue()


def audio_callback(indata, frames, time_info, status):
    """
    마이크에서 들어오는 오디오 블록을 계속 queue에 넣는 콜백.
    로봇이 말하는 중이면(is_speaking=True) 입력 무시.
    """
    if is_speaking.is_set():
        return
    audio_q.put(indata.copy())


def start_stream():
    """
    실시간 마이크 스트림 시작.
    main에서 한 번만 호출해서 유지.
    """
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        blocksize=BLOCK_SIZE,
        callback=audio_callback
    )
    stream.start()
    return stream


def get_next_utterance():
    """
    사람의 '한 문장'이 끝날 때까지 기다렸다가,
    그 문장에 해당하는 오디오 데이터를 numpy 배열로 반환.
    (무한 루프 안에서 호출하면, 말할 때마다 한 번씩 반환됨)
    """
    current_chunks = []
    is_active = False
    last_voice_time = 0.0

    while True:
        block = audio_q.get()   # 새 오디오 블록 기다림 (blocking)
        rms = float(np.sqrt(np.mean(block**2)))
        now = time.time()

        # 말하는 중 (소리가 threshold보다 큼)
        if rms > SILENCE_THRESHOLD:
            if not is_active:
                current_chunks = []
                is_active = True
            last_voice_time = now
            current_chunks.append(block)

        # 말하던 중이었고, 일정 시간 이상 조용하면 → 문장 종료
        if is_active and (now - last_voice_time > SILENCE_DURATION):
            is_active = False
            if current_chunks:
                audio_data = np.concatenate(current_chunks, axis=0)
                current_chunks = []
                return audio_data
            # current_chunks 비었으면 그냥 다시 루프
