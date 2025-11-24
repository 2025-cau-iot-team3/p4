# wakeword.py

import re


def is_wake_word(text: str) -> bool:
    """
    '모모야'를 말했을 때 Whisper가 이상하게 인식한 경우까지
    웨이크워드로 인정해 주는 함수
    """
    if not text:
        return False

    # 공백, 마침표, 물음표, 느낌표 제거
    t = re.sub(r"[\s\.\?\!]", "", text)

    wake_patterns = [
        "모모야",   # 정상 인식
        "뭐뭐야",
        "뭐모야",
        "모뭐야",
        "머머야",
        "머모야",
        "모머야",
        "뭐머야",
        "머뭐야",
        "뭐뭐해",
        "뭐해",
        "뭐요",
        "너무요",
    ]

    for pat in wake_patterns:
        if pat in t:
            return True

    return False
