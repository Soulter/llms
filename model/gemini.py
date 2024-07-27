from ._model import Model, retry
import google.generativeai as genai


class GeminiClient(Model):
    def __init__(self, api_key: str) -> None:
        super().__init__()
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = self.model.start_chat(history=[])

    @retry(3)
    async def text_chat(self, prompt: str, session_id: str, image_url: str = None, **kwargs) -> str:
        return self.chat.send_message(prompt).text

    @retry(3)
    async def forget(self, session_id=None) -> bool:
        self.chat.history = []