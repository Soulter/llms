from ._model import Model, retry
from .._sydney import create_conversation, ask_stream, upload_image

class NewbingClient(Model):
    def __init__(self, cookies, proxy) -> None:
        super().__init__()
        self.cookies = cookies
        self.proxy = proxy
        self.is_search = True

    @retry(3)
    async def create_conversation(self):
        self.c = await create_conversation(proxy=self.proxy, cookies=self.cookies)
        return self.c

    @retry(3)
    async def text_chat(self, prompt: str, session_id: str, image_url: str = None, **kwargs) -> str:
        ret = "error"
        async for resp in ask_stream(self.c, prompt, "", proxy=self.proxy, cookies=self.cookies, image_url=image_url, no_search=not self.is_search):
            print(resp)
            if resp['type'] == 2:
                try:
                    ret = resp['item']['result']['message']
                except:
                    ret = "json error"
                break

        try:
            self.c = self.create_conversation()
        except Exception as e:
            print(e)

        return ret
    
    @retry(3)
    async def _upload_image(self, filename: str) -> str:
        bcid = await upload_image(filename, proxy=self.proxy)
        url = "https://www.bing.com/images/blob?bcid=" + bcid
        print("[llms/newbing] uploaded image url: ", url)
        return url
    
    async def set_search(self, is_search: bool):
        self.is_search = is_search
    
    @retry(3)
    async def forget(self):
        self.c = None
        await self.create_conversation()