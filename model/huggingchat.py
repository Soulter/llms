from ._model import Model, retry
from hugchat import hugchat
from hugchat.login import Login

class HuggingChatClient(Model):
    def __init__(self, email: str, pwd: str, path: str) -> None:
        super().__init__()
        sign = Login(email, pwd)
        cookies = sign.login()
        sign.saveCookiesToDir(path)
        self.hc_client = hugchat.ChatBot(cookies=cookies.get_dict())
        self.hc_cid = self.hc_client.new_conversation()
        self.hc_client.change_conversation(self.hc_cid)

    @retry(3)
    def text_chat(self, prompt: str) -> str:
        return self.claude_client.send_message(prompt, self.claude_cid)['text']
    
    @retry(3)
    def reset_chat(self):
        self.claude_cid = self.claude_client.create_new_chat()['uuid']