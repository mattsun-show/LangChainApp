class PromptsLoader:
    def web_summarize(self, content: str, n_chars: int = 300) -> str:
        prompt = f"""以下はとあるWebページのコンテンツです。内容を{n_chars}字程度でわかりやすく要約してください。

========

{content[:1000]}

========

日本語で書いください。
"""
        return prompt

    def youtube_summarize_template(self) -> str:
        prompt = """Write a concise Japanese summary of the following transcript of Youtube Video.

{text}

ここから日本語で書いてね:
"""
        return prompt
