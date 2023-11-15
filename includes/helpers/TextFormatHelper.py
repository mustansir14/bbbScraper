import re
import html


class TextFormatHelper:
    @staticmethod
    def html2text(text: str | None) -> str:
        if not text:
            return ""

        text = text.replace("\r", "")
        text = html.unescape(text)
        text = re.sub(r'<br[^>]*?>', "\n", text)
        text = re.sub(r'\n{2,}', "\n\n", text)

        return text
