import wave

import simpleaudio as sa
from piper import PiperVoice

# https://huggingface.co/rhasspy/piper-voices/tree/main/fr/fr_FR/siwis/medium
voice = PiperVoice.load("dl/fr_FR-siwis-medium.onnx")


def synthesize_and_play(text, wav_path="out.wav"):
    with wave.open(wav_path, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)

    wave_obj = sa.WaveObject.from_wave_file(wav_path)
    play_obj = wave_obj.play()
    play_obj.wait_done()
