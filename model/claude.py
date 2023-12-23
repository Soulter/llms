from ._model import Model, retry
from .._claude_api import Client

class ClaudeClient(Model):
    def __init__(self, cookie: str) -> None:
        super().__init__()
        self.claude_client = Client(cookie=cookie)
        self.claude_cid = self.claude_client.create_new_chat()['uuid']

    @retry(3)
    def text_chat(self, prompt: str) -> str:
        return self.claude_client.send_message(prompt, self.claude_cid)
    
    @retry(3)
    def reset_chat(self):
        self.claude_cid = self.claude_client.create_new_chat()['uuid']