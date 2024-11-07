# sentiment_analysis.py
import torch
from transformers import BertTokenizer, BertForSequenceClassification

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
    predicted_label = torch.argmax(logits, dim=1).item()

    # 感情ラベル
    emotion_labels = ["Super Negative", "Negative", "Neutral", "Positive", "Super Positive"]
    predicted_emotion = emotion_labels[predicted_label]

    return {
        "text": text,
        "voltage": predicted_label,
        "classification": predicted_emotion
    }
