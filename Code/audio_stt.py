# audio_stt.py

import warnings
import whisper
import numpy as np
from scipy.io.wavfile import write

from config import SAMPLE_RATE, DEVICE, CMD_MODEL_NAME

warnings.filterwarnings("ignore")


def load_cmd_model():
    """
    명령 인식용 Whisper 모델 로드
    """
    print(f"[시스템] Whisper 명령 모델 로딩 중... (device={DEVICE}, model={CMD_MODEL_NAME})")
    model = whisper.load_model(CMD_MODEL_NAME, device=DEVICE)
    print("[시스템] Whisper 명령 모델 로딩 완료.")
    return model


def transcribe_audio_from_array(model, audio_data: np.ndarray) -> str:
    """
    numpy 오디오 배열 → WAV 파일 → Whisper STT
    """
    if audio_data is None or len(audio_data) == 0:
        return ""

    wav_path = "mic_stream_cmd.wav"
    write(wav_path, SAMPLE_RATE, (audio_data * 32767).astype(np.int16))

    result = model.transcribe(
        wav_path,
        language="ko",
        fp16=(DEVICE == "cuda"),
        temperature=0.0,
        condition_on_previous_text=False
    )

    return result["text"].strip()
