from nakuru.entities.components import *
from util import cmd_config as cc
import traceback
from .model._model import Model
from .model.huggingchat import HuggingChatClient
from .model.claude import ClaudeClient
import os
from cores.qqbot.global_object import AstrMessageEvent, CommandResult
flag_not_support = False
try:
    from util.plugin_dev.api.v1.config import *
except ImportError:
    flag_not_support = True
    print("llms: 导入接口失败。请升级到 astrbot 最新版本。")

"""
AstrBot (原 QQChannelChatGPT) 的大语言模型库插件。
"""
class LLMSPlugin:
    """
    初始化函数, 可以选择直接pass
    """
    def __init__(self) -> None:
        print("LLMSPlugin")
        self.NAMESPACE = "astrbot_plugin_llms"
        self.cc = cc.CmdConfig()
        # self.cc.init_attributes(["llms_claude_cookie", "llms_huggingchat_email", "llms_huggingchat_psw", "llms_choice"], "")
        put_config(self.NAMESPACE, "llms_claude_cookie", "llms_claude_cookie", "", "Claude 的 Cookie")
        put_config(self.NAMESPACE, "llms_huggingchat_email", "llms_huggingchat_email", "", "HuggingChat 的邮箱")
        put_config(self.NAMESPACE, "llms_huggingchat_psw", "llms_huggingchat_psw", "", "HuggingChat 的密码")
        self.cfg = load_config(self.NAMESPACE)
        self.curr_llm = None
        self.curr_client: Model = None

    def run(self, ame: AstrMessageEvent):
        message = ame.message_str
        if self.curr_llm is not None:
            if self.curr_client is None:
                return CommandResult(
                    hit=True,
                    success=False,
                    message_chain=[Plain("LLM 插件错误：当前语言模型为 None。")],
                    command_name="llm"
                )
            try:
                resp = self.curr_client.text_chat(message)
                return CommandResult(
                    hit=True,
                    success=True,
                    message_chain=[Plain(resp)],
                    command_name="llm"
                )
            except BaseException as e:
                traceback.print_exc()
                return CommandResult(
                    hit=True,
                    success=False,
                    message_chain=[Plain(f"LLM 插件错误：{str(e)}")],
                    command_name="llm"
                )
        
        elif message.lower().startswith("llm") or message.lower().startswith("/llm"):
            l = message.split(" ")
            
            if len(l) == 1:
                return CommandResult(
                    hit=True,
                    success=True,
                    message_chain=[Plain(self.help_menu())],
                    command_name="llm"
                )
                
            if l[1] == "0":
                self.curr_llm = None
                return CommandResult(
                    hit=True,
                    success=True,
                    message_chain=[Plain("成功关闭 LLMS 插件。")],
                    command_name="llm"
                )
            
            # Claude -> Setting
            elif l[1] == "1":
                # claude_cookie = self.cc.get("llms_claude_cookie", "")
                claude_cookie = self.cfg["llms_claude_cookie"]
                if claude_cookie == "":
                    return True, tuple([True, "Claude 未被启用：未填写 Claude cookies。请使用\n\n/llm claude [您在Claude上的的Cookie]\n\n以激活。(或在可视化面板修改)", "llm"])
                try:
                    self.curr_client = ClaudeClient(claude_cookie)
                    self.curr_llm = "claude"
                    return True, tuple([True, "成功启用 Claude。", "llm"])
                except BaseException as e:
                    return True, tuple([True, f"Claude 未被启用。可能因为您的 Claude 的 Cookie 不正确。\n\n报错堆栈: {traceback.format_exc()}", "llm"])
            
            # HuggingChat -> Setting
            elif l[1] == "2":
                # email = self.cc.get("llms_huggingchat_email", "")
                # psw = self.cc.get("llms_huggingchat_psw", "")
                email = self.cfg["llms_huggingchat_email"]
                psw = self.cfg["llms_huggingchat_psw"]
                if email == "" or psw == "":
                    return True, tuple([True, "HuggingChat 未被启用：未填写 HuggingChat 账号，请使用\n\n/llm hc [您的邮箱] [您的密码]\n\n以激活。(或在可视化面板修改)", "llm"])
                try:
                    root_path = os.path.dirname(__file__)
                    data_path = os.path.join(root_path, "data")
                    file_path = os.path.join(data_path, "llms_huggingchat_cookies.json")
                    self.curr_client = HuggingChatClient(email, psw, file_path)
                    self.curr_llm = "huggingchat"
                    return True, tuple([True, "成功启用 HuggingChat。", "llm"])
                except BaseException as e:
                    return True, tuple([True, f"HuggingChat 未被启用。可能因为 HuggingChat 账号不正确。\n\n报错堆栈: {traceback.format_exc()}", "llm"])
                
            elif l[1] == "claude" and len(l) >= 3:
                cookies_str = "".join(l[2:])
                # self.cc.put("llms_claude_cookie", cookies_str)
                update_config(self.NAMESPACE, "llms_claude_cookie", cookies_str)
                return True, tuple([True, "成功设置 Claude Cookie。", "llm"])
            elif l[1] == "hc" and len(l) == 4:
                email = l[2]
                psw = l[3]
                # self.cc.put("llms_huggingchat_email", email)
                # self.cc.put("llms_huggingchat_psw", psw)
                update_config(self.NAMESPACE, "llms_huggingchat_email", email)
                update_config(self.NAMESPACE, "llms_huggingchat_psw", psw)
                return True, tuple([True, "成功设置 HuggingChat 账号。", "llm"])

            elif l[1] == "reset":
                try:
                    self.curr_client.reset_chat()
                    return True, tuple([True, f"成功重置 {self.curr_llm} 会话。", "llm"])
                except BaseException as e:
                    return True, tuple([True, f"重置 {self.curr_llm} 会话失败：{str(e)}", "llm"])
            
            else:
                return True, tuple([True, self.help_menu(), "llm"])
        else:
            return False, None
            
    def help_menu(self):
        return f"=======LLMS V1.2=======\n目前支持: \n0. 不启用\n1. Claude\n2. HuggingChat\n指令: \n /llm [序号]: 切换到对应的语言模型。\n /llm reset: 重置会话\n\n当前启用的是: {self.curr_llm}"

    # 检查权限
    def check_auth(self, message_obj, platform, model_name, role):
        if role != "admin":
            return False, True, tuple([True, f"您的权限级别{role}没有权限设置{model_name}模型。请联系机器人部署者。", "llm"])
        return True, None, None

    """
    帮助函数,当用户输入 plugin v 插件名称 时,会调用此函数,返回帮助信息
    返回参数要求(必填): dict{
        "name": str, # 插件名称
        "desc": str, # 插件简短描述
        "help": str, # 插件帮助信息
        "version": str, # 插件版本
        "author": str, # 插件作者
    }
    """        
    def info(self):
        return {
            "plugin_type": "llm",
            "name": "astrbot_plugin_llms",
            "desc": "支持 Claude、HuggingChat、Gemini。主页: https://github.com/Soulter/llms",
            "help": "前往 https://github.com/Soulter/llms 查看帮助",
            "version": "v1.2",
            "author": "Soulter"
        }
