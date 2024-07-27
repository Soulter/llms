from ._model import Model, retry
from hugchat import hugchat
from hugchat.login import Login

class HuggingChatClient(Model):
    def __init__(self, email: str, pwd: str, path: str) -> None:
        super().__init__()
        sign = Login(email, pwd)
        print("HuggingChatClient init")
        cookies = sign.login()
        sign.saveCookiesToDir(path)
        self.hc_client = hugchat.ChatBot(cookies=cookies.get_dict())
        self.hc_cid = self.hc_client.new_conversation()
        self.hc_client.change_conversation(self.hc_cid)
        self.is_search = False
        print("HuggingChatClient init done")

    @retry(3)
    async def text_chat(self, prompt: str, session_id: str, image_url: str = None, **kwargs) -> str:
        return self.hc_client.chat(prompt, web_search=self.is_search)
    
    async def set_search(self, is_search: bool):
        self.is_search = is_search
    
    @retry(3)
    async def forget(self, session_id=None) -> bool:
        conv = self.hc_client.new_conversation()
        self.hc_client.change_conversation(conv)