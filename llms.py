import logging
from .model._model import Model
from .model.huggingchat import HuggingChatClient
from .model.claude import ClaudeClient
from .model.gemini import GeminiClient
from .model.newbing import NewbingClient
flag_not_support = False
try:
    from util.plugin_dev.api.v1.config import *
    from util.plugin_dev.api.v1.bot import (
        PluginMetadata,
        PluginType,
        AstrMessageEvent,
        CommandResult,
        Context
    )
    from util.plugin_dev.api.v1.register import register_llm, unregister_llm
except ImportError:
    flag_not_support = True
    print("llms: 导入接口失败。请升级到 AstrBot 最新版本。")


class LLMSPlugin:
    def __init__(self, context: Context) -> None:
        self.NAMESPACE = "astrbot_plugin_llms"
        put_config(self.NAMESPACE, "llms_claude_cookie", "llms_claude_cookie", "", "Claude 的 Cookie")
        put_config(self.NAMESPACE, "llms_huggingchat_email", "llms_huggingchat_email", "", "HuggingChat 的邮箱")
        put_config(self.NAMESPACE, "llms_huggingchat_psw", "llms_huggingchat_psw", "", "HuggingChat 的密码")
        put_config(self.NAMESPACE, "llms_gemini_api_key", "llms_gemini_api_key", "", "Gemini 的 API Key")
        put_config(self.NAMESPACE, "llms_newbing_cookies", "llms_newbing_cookies", "", "NewBing 的 Cookies 不要在这里填写，请添加到 data/newbing_cookies.json 文件下。")
        self.cfg = load_config(self.NAMESPACE)
        self.context = context
        self.curr_client: Model = None
        self.proxy = self.context.config_helper.https_proxy
        self.models = ["claude", "huggingchat", "gemini", "newbing"]
        self.logger = logging.getLogger("astrbot")
        
        self.context.register_commands(self.NAMESPACE, "llms", "配置 LLMS 支持的语言模型。", 10, self.llms_handler)
        
        self.load(context)
        
    def load(self, context: Context):
        if self.cfg["llms_claude_cookie"]:
            client = ClaudeClient(self.cfg["llms_claude_cookie"])
            context.register_provider("claude", client, self.NAMESPACE)
        if self.cfg["llms_huggingchat_email"] and self.cfg["llms_huggingchat_psw"]:
            client = HuggingChatClient(self.cfg["llms_huggingchat_email"], self.cfg["llms_huggingchat_psw"], "")
            context.register_provider("huggingchat", client, self.NAMESPACE)
        if self.cfg["llms_gemini_api_key"]:
            client = GeminiClient(self.cfg["llms_gemini_api_key"])
            context.register_provider("gemini", client, self.NAMESPACE)
        if self.cfg["llms_newbing_cookies"]:
            client = NewbingClient(self.cfg["llms_newbing_cookies"], self.proxy)
            context.register_provider("newbing", client, self.NAMESPACE)
        
    async def llms_handler(self, ame: AstrMessageEvent, context: Context):
        if flag_not_support:
            return CommandResult().message("llms: 导入接口失败。请升级到 AstrBot 最新版本。")
        
        tokens = ame.message_str.split(" ")
        if len(tokens) == 1:
            # llm
            return CommandResult().message(self.help_menu())

    def help_menu(self):
        return f"""=======LLMS V1.3=======

支持的语言模型: {", ".join(self.models)}

请在 AstrBot 面板中配置所需的语言模型。"""

    def info(self):
        return PluginMetadata(
            plugin_name="astrbot_plugin_llms",
            plugin_type=PluginType.LLM,
            author="Soulter",
            desc="支持 Claude、HuggingChat、Gemini。主页: https://github.com/Soulter/llms",
            version="v1.3.0",
            repo="https://github.com/Soulter/llms"
        )
