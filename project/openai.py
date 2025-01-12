from transformers import AutoModelForCausalLM, AutoTokenizer
import re

def remove_duplicates(text):
    """
    文やフレーズの繰り返しを検出して削除します。
    """
    # 文ごとに分割して、重複を削除
    sentences = text.split("。")
    seen_sentences = set()
    unique_sentences = []

    for sentence in sentences:
        if sentence and sentence not in seen_sentences:
            unique_sentences.append(sentence)
            seen_sentences.add(sentence)

    # 文を再結合
    cleaned_text = "。".join(unique_sentences)

    # フレーズの繰り返しを削除 (例: "あなたがストレスを解消するのに...")
    cleaned_text = re.sub(r"(。?([^。]+?)\2{2,})", r"\2", cleaned_text)

    return cleaned_text.strip()

def generate_stress_relief_suggestion(emotion, text):
    """
    感情と音声テキストに基づいてストレス解消方法を提案します。
    """
    model_name = "rinna/japanese-gpt2-medium"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # プロンプトを作成
    prompt = f"""
    以下は感情分析結果に基づく音声テキストです:
    感情: {emotion}
    テキスト: "{text}"
    
    感情が{emotion}の場合、ストレスを解消するために提案できる具体的な方法をいくつか挙げてください。可能であればポジティブなアクションを提案してください。
    """
    
    # モデルにプロンプトを入力して生成
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    output = model.generate(input_ids, max_length=77, num_return_sequences=1, pad_token_id=tokenizer.eos_token_id)
    
    # モデル出力をデコード
    suggestion = tokenizer.decode(output[0], skip_special_tokens=True)
    
    # プロンプト部分を削除
    if prompt.strip() in suggestion:
        suggestion = suggestion.replace(prompt.strip(), "").strip()
    
    # 重複部分を削除
    suggestion = remove_duplicates(suggestion)

    return suggestion.strip()

