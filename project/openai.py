import openai
def generate_stress_relief_suggestion(emotion, text):
    """
    感情と音声テキストに基づき、OpenAIでストレス発散方法を生成する。
    """
    prompt = f"""
    以下は感情分析結果に基づく音声テキストです:
    感情: {emotion}
    テキスト: "{text}"
    
    感情が{emotion}の場合、ストレスを解消するために提案できる具体的な方法をいくつか挙げてください。可能であればポジティブなアクションを提案してください。
    """
    
    try:
        response = openai.Completion.create(
            model="gpt-4o",  # 使用するOpenAIモデル
            messages=[
                {"role": "system", "content": "あなたは役立つアシスタントです。"},
                {"role": "user", "content": prompt},
            ],
            prompt=prompt,
            max_tokens=150,
            temperature=0.7,
        )
        suggestion = response.choices[0].text.strip()
        return suggestion
    except Exception as e:
        print(f"Error generating suggestion: {e}")
        return "ストレス発散方法を生成できませんでした。"
