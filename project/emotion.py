import librosa
import numpy as np
import tensorflow as tf
import os

# 感情ラベル
emotion_labels = {0: 'happy', 1: 'sad', 2: 'angry', 3: 'neutral'}

# 音声から特徴量を抽出する関数
def extract_features(file_path):
    y, sr = librosa.load(file_path, sr=16000)
    mel_spec = librosa.feature.melspectrogram(y, sr=sr, n_mels=128)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    mel_spec_db = np.expand_dims(mel_spec_db, axis=-1)  # (時間, 周波数, 1)
    return mel_spec_db

# モデルの読み込み
def load_model():
    if not os.path.exists('emotion_model.h5'):
        raise FileNotFoundError("Model file not found. Please train the model first.")
    model = tf.keras.models.load_model('emotion_model.h5')
    return model

# 感情分析の実行
def predict_emotion(model, mel_spec):
    mel_spec = np.expand_dims(mel_spec, axis=0)  # バッチ次元を追加
    predictions = model.predict(mel_spec)
    emotion_label = np.argmax(predictions)
    return emotion_labels[emotion_label]
