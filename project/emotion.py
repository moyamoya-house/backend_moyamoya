# sentiment_analysis.py
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import torch.nn.functional as F
# 感情分析モデルとTokenizerの準備
model_name = 'nlptown/bert-base-multilingual-uncased-sentiment'
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name)

# 感情分析関数
def analyze_sentiment(text):
    # テキストのトークナイズ
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    
    # モデルで推論
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits

    # ソフトマックス関数でスコアを確率に変換
    probabilities = F.softmax(logits, dim=1).squeeze()

    # スコアに基づく感情ラベルの予測
    predicted_label = torch.argmax(probabilities).item()
    emotion_labels = ["超ネガティブ", "ネガティブ", "ニュートラル", "ポジティブ", "超ポジティブ"]
    predicted_emotion = emotion_labels[predicted_label]

    # `voltage` の詳細化 - 予測されたクラスの確率値
    voltage = probabilities[predicted_label].item()  # 0 から 1 の範囲で出力されます

    return {
        "text": text,
        "voltage": voltage,
        "classification": predicted_emotion,
        "predicted": predicted_label
    }