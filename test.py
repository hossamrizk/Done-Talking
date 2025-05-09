from TTS.api import TTS

# Initialize XTTS v2 (supports Arabic)
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True)

# Generate Arabic speech
tts.tts_to_file(
    text="مرحبا بك في نظام تحويل النص إلى كلام", # Need 1 reference audio
    language="ar",
    file_path="arabic_output.wav"
)