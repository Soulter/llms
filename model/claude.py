from typing import Any, Coroutine
from ._model import Model, retry
from .._claude_api import Client

class ClaudeClient(Model):
    def __init__(self, cookie: str) -> None:
        super().__init__()
        self.claude_client = Client(cookie=cookie)
        self.claude_cid = self.claude_client.create_new_chat()['uuid']

    @retry(3)
    async def text_chat(self, prompt: str, session_id: str, image_url: str = None, **kwargs) -> Coroutine[Any, Any, str]:
        return self.claude_client.send_message(prompt, self.claude_cid)
    
    @retry(3)
    async def forget(self, session_id=None) -> bool:
        self.claude_cid = self.claude_client.create_new_chat()['uuid']