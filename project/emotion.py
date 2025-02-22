from textblob import TextBlob
from deep_translator import GoogleTranslator

def translate_to_english(text):
    """ 日本語のテキストを英語に翻訳 """
    return GoogleTranslator(source="ja", target="en").translate(text)

def analyze_sentiment(text):
    """ 日本語の感情分析（Google翻訳 + TextBlob） """
    # 日本語を英語に翻訳
    translated_text = translate_to_english(text)
    
    # TextBlob で感情分析
    blob = TextBlob(translated_text)
    polarity = blob.sentiment.polarity  # -1（ネガティブ）〜 1（ポジティブ）

    # 感情の分類
    if polarity <= -0.6:
        predicted_emotion = "超ネガティブ"
        predicted_label = 0
    elif polarity < -0.2:
        predicted_emotion = "ネガティブ"
        predicted_label = 1
    elif polarity < 0.2:
        predicted_emotion = "ニュートラル"
        predicted_label = 2
    elif polarity < 0.6:
        predicted_emotion = "ポジティブ"
        predicted_label = 3
    else:
        predicted_emotion = "超ポジティブ"
        predicted_label = 4

    voltage = abs(polarity)  # 0〜1 の範囲

    return {
        "text": text,
        "voltage": voltage,
        "classification": predicted_emotion,
        "predicted": predicted_label
    }