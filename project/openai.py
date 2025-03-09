import google.generativeai as genai
import re

def remove_duplicates(text):
    """
    文やフレーズの繰り返しを検出して削除します。
    """
    sentences = text.split("。")
    seen_sentences = set()
    unique_sentences = []

    for sentence in sentences:
        if sentence and sentence not in seen_sentences:
            unique_sentences.append(sentence)
            seen_sentences.add(sentence)

    cleaned_text = "。".join(unique_sentences)
    cleaned_text = re.sub(r"(。?([^。]+?)\2{2,})", r"\2", cleaned_text)
    
    return cleaned_text.strip()

def generate_stress_relief_suggestion(emotion, text):
    """
    感情と音声テキストに基づいてストレス解消方法を提案します。
    """
    genai.configure(api_key="AIzaSyCwB3sQ")
    model = genai.GenerativeModel("gemini-1.5-pro-latest")

    prompt = f"""
    以下は感情分析結果に基づく音声テキストです:
    感情: {emotion}
    テキスト: "{text}"
    
    感情が{emotion}の場合、ストレスを解消するために提案できる具体的な方法をいくつか挙げてください。可能であればポジティブなアクションを提案してください。
    """
    
    try:
        response = model.generate_content(prompt)
        suggestion = response.text.strip()
        suggestion = remove_duplicates(suggestion)
        return suggestion
    except Exception as e:
        return f"Error: {str(e)}"
