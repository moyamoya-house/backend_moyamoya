import librosa
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# 感情ラベル
emotion_labels = {0: 'happy', 1: 'sad', 2: 'angry', 3: 'neutral'}

# 音声から特徴量を抽出する関数
def extract_features(file_path):
    y, sr = librosa.load(file_path, sr=16000)
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    mel_spec_db = np.expand_dims(mel_spec_db, axis=-1)  # (時間, 周波数, 1)
    return mel_spec_db

# 感情分析モデルの構築
def build_model(input_shape, num_classes):
    model = models.Sequential()
    model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Flatten())
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(num_classes, activation='softmax'))
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def train_model():
    X = []  # 音声の特徴量
    y = []  # 感情ラベル

    # サンプルデータの準備
    for i in range(100):  # 100個のデータを仮に用意
        X.append(np.random.rand(128, 128, 1))  # ランダムなメルスペクトログラムデータ
        y.append(np.random.randint(0, 4))  # 0〜3のランダムな感情ラベル

    X = np.array(X)
    y = to_categorical(np.array(y), num_classes=4)

    # 訓練データとテストデータに分割
    if len(X) > 1:  # データが複数ある場合のみ分割
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    else:
        X_train, X_test, y_train, y_test = X, X, y, y  # データが1つしかない場合は分割しない

    # モデルの構築
    input_shape = X_train[0].shape
    num_classes = 4
    model = build_model(input_shape, num_classes)

    # モデルのトレーニング
    model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))

    # モデルを保存
    model.save('emotion_model.h5')

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

if __name__ == "__main__":
    train_model()
