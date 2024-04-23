from ._model import Model, retry
from .._sydney import create_conversation, ask_stream

class NewbingClient(Model):
    def __init__(self, cookies, proxy) -> None:
        super().__init__()
        self.cookies = cookies
        self.proxy = proxy

    @retry(3)
    async def create_conversation(self):
        self.c = await create_conversation(proxy=self.proxy, cookies=self.cookies)
        return self.c

    @retry(3)
    async def text_chat(self, prompt: str) -> str:
        ret = "error"
        async for resp in ask_stream(self.c, prompt, "", proxy=self.proxy, cookies=self.cookies):
            # print(resp)
            if resp['type'] == 2:
                try:
                    ret = resp['item']['result']['message']
                except:
                    ret = "json error"
                break

        return ret
    
    @retry(3)
    async def forget(self):
        self.c = None
        await self.create_conversation()