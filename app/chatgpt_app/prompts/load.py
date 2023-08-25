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

    def web_summarize_map_template(self) -> str:
        prompt = """あなたの仕事は与えられた文章から重要なエッセンスを抽出することです。文章が与えられた場合、重要なエッセンスを箇条書きにして、日本語で書き出してください。
========
{text}
========
"""
        return prompt

    def web_summarize_combine_template(self) -> str:
        prompt = """あなたの仕事はニュース原稿を書くことです。
        メモを元に、{n_chars}文字程度で、ニュースの原稿をわかりやすく論理的に敬語で書いてください。
========
メモ:{{text}}
========
"""
        return prompt

    def web_summarize_refine_template(self) -> str:
        prompt = """以下はとあるWebページのコンテンツです。内容を{n_chars}字程度でわかりやすく要約してください。
========
メモ:{{text}}
========
日本語で書いください。
"""
        return prompt
