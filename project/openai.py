from transformers import AutoModelForCausalLM, AutoTokenizer

def remove_duplicates(text):
    # 単語や文の繰り返しを取り除く
    sentences = text.split('。')
    seen = set()
    result = []
    for sentence in sentences:
        if sentence not in seen:
            result.append(sentence)
            seen.add(sentence)
    return '。'.join(result)

def generate_stress_relief_suggestion(emotion, text):
    model_name = "rinna/japanese-gpt2-medium"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    prompt = f"""
    以下は感情分析結果に基づく音声テキストです:
    感情: {emotion}
    テキスト: "{text}"
    
    感情が{emotion}の場合、ストレスを解消するために提案できる具体的な方法をいくつか挙げてください。可能であればポジティブなアクションを提案してください。
    """
    
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    output = model.generate(input_ids, max_length=150, num_return_sequences=1, pad_token_id=tokenizer.eos_token_id)
    
    suggestion = tokenizer.decode(output[0], skip_special_tokens=True)
    
    # 重複部分を削除
    suggestion = remove_duplicates(suggestion)

    return suggestion.strip()
