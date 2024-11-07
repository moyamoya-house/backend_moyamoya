from pydub import AudioSegment
import speech_recognition as sr

# 音声ファイルをテキストに変換
def transcribe_audio(file_path):
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_file(file_path)
    audio = audio.set_frame_rate(16000)  # サンプリングレートを設定

    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language="ja")  # 日本語指定
    return text