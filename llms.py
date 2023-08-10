from nakuru.entities.components import *
from nakuru import (
    GroupMessage,
    FriendMessage
)
from botpy.message import Message, DirectMessage
from model.platform.qq import QQ
import time
import threading
from util import cmd_config as cc

try:
    from claude_api import Client
    from hugchat import hugchat
    from hugchat.login import Login
except ImportError as e:
    print("===== LLMS插件依赖的Claude和HuggingChat库未安装。请先安装或更新claude_api和hugchat =====")
    raise e


"""
QQChannelChatGPT的大语言模型库插件。
"""
class LLMSPlugin:
    """
    初始化函数, 可以选择直接pass
    """
    def __init__(self) -> None:
        print("LLMSPlugin")
        self.cc = cc.CmdConfig()
        self.cc.init_attributes(["llms_claude_cookie", "llms_huggingchat_email", "llms_huggingchat_psw", "llms_choice"], "")
        self.curr_llm = None
        self.claude_client = None
        self.hc_client = None
        self.claude_cid = None
        self.hc_cid = None

    """
    入口函数，机器人会调用此函数。
    参数规范: message: 消息文本; role: 身份; platform: 消息平台; message_obj: 消息对象; qq_platform: QQ平台对象，可以通过调用qq_platform.send()直接发送消息。详见Helloworld插件示例
    参数详情: role为admin或者member; platform为qqchan或者gocq; message_obj为nakuru的GroupMessage对象或者FriendMessage对象或者频道的Message, DirectMessage对象。
    返回规范: bool: 是否hit到此插件(所有的消息均会调用每一个载入的插件, 如果没有hit到, 则应返回False)
             Tuple: None或者长度为3的元组。当没有hit到时, 返回None. hit到时, 第1个参数为指令是否调用成功, 第2个参数为返回的消息文本或者gocq的消息链列表, 第3个参数为指令名称
    例子：做一个名为"yuanshen"的插件；当接收到消息为“原神 可莉”, 如果不想要处理此消息，则返回False, None；如果想要处理，但是执行失败了，返回True, tuple([False, "请求失败啦~", "yuanshen"])
          ；执行成功了，返回True, tuple([True, "结果文本", "yuanshen"])
    """
    def run(self, message: str, role: str, platform: str, message_obj, qq_platform: QQ):

        if message.lower().startswith("llm") or message.lower().startswith("/llm"):
            l = message.split(" ")
            
            if len(l) == 1:
                return True, tuple([True, self.help_menu(), "llm"])
                
            if l[1] == "0":
                self.curr_llm = None
                return True, tuple([True, "成功关闭LLMS插件，启用项目默认设置。", "llm"])
            elif l[1] == "1":
                if platform == "gocq":
                    if(str(message_obj.sender.user_id) != self.cc.get("admin_qq", 0)):
                            return True, tuple([True, "您没有权限设置Claude Cookie。", "llm"])
                claude_cookie = self.cc.get("llms_claude_cookie", "")
                if claude_cookie == "":
                    return True, tuple([True, "Claude插件未被启用。因为您未填写claude的cookie，请机器人管理员先私聊机器人发送\n\n/llm claude [您在Claude上的的Cookie]\n\n以激活。(或者在cmd_config文件内修改)", "llm"])
                try:
                    self.claude_client = Client(claude_cookie)
                    self.claude_cid = self.claude_client.create_new_chat()['uuid']
                    self.curr_llm = "claude"
                    return True, tuple([True, "成功启用LLMS插件，启用Claude模型，将在下次回答生效！", "llm"])
                except BaseException as e:
                    return True, tuple([True, f"Claude插件未被启用。可能因为您的Claude的Cookie不正确。报错原因：{str(e)}", "llm"])
                
            elif l[1] == "2":
                if platform == "gocq":
                    if(str(message_obj.sender.user_id) != self.cc.get("admin_qq", 0)):
                        return True, tuple([True, "您没有权限设置HuggingChat的账号。", "llm"])
                
                email = self.cc.get("llms_huggingchat_email", "")
                psw = self.cc.get("llms_huggingchat_psw", "")
                if email == "" or psw == "":
                    return True, tuple([True, "HuggingChat插件未被启用。因为您未填写HuggingChat的账号，请机器人管理员先私聊机器人发送\n\n/llm hc [您的邮箱] [您的密码]\n\n以激活。(或者在cmd_config文件内修改)", "llm"])
                try:
                    sign = Login(email, psw)
                    cookies = sign.login()
                    cookie_path_dir = "./llms_huggingchat_cookies"
                    sign.saveCookiesToDir(cookie_path_dir)
                    self.hc_client = hugchat.ChatBot(cookies=cookies.get_dict())
                    self.hc_cid = self.hc_client.new_conversation()
                    self.hc_client.change_conversation(self.hc_cid)
                    self.curr_llm = "huggingchat"
                    return True, tuple([True, "成功启用LLMS插件，启用HuggingChat模型，将在下次回答生效！", "llm"])
                except BaseException as e:
                    return True, tuple([True, f"HuggingChat插件未被启用。可能因为您的HuggingChat的账号不正确。报错原因：{str(e)}", "llm"])

            elif l[1] == "claude" and len(l) >= 3:
                if platform == "gocq":
                    if(str(message_obj.sender.user_id) != self.cc.get("admin_qq", 0)):
                        return True, tuple([True, "您没有权限设置Claude的Cookie。", "llm"])
                cookies_str = "".join(l[2:])
                self.cc.put("llms_claude_cookie", cookies_str)
                return True, tuple([True, "成功设置Claude的Cookie，您现在可以启用Claude了。", "llm"])
            elif l[1] == "hc" and len(l) == 4:
                if platform == "gocq":
                    if(str(message_obj.sender.user_id) != self.cc.get("admin_qq", 0)):
                        return True, tuple([True, "您没有权限设置HuggingChat的账号。", "llm"])
                email = l[2]
                psw = l[3]
                self.cc.put("llms_huggingchat_email", email)
                self.cc.put("llms_huggingchat_psw", psw)
                return True, tuple([True, "成功设置HuggingChat的账号，您现在可以启用HuggingChat了。", "llm"])
            
            elif l[1] == "reset":
                if self.curr_llm == "claude":
                    try:
                        self.claude_cid = self.claude_client.create_new_chat()['uuid']
                        return True, tuple([True, "成功重置Claude会话。", "llm"])
                    except BaseException as e:
                        return True, tuple([True, f"Claude会话重置失败。报错原因：{str(e)}", "llm"])
                    
                elif self.curr_llm == "huggingchat":
                    try:
                        self.hc_cid = self.hc_client.new_conversation()
                        self.hc_client.change_conversation(self.hc_cid)
                        return True, tuple([True, "成功重置HuggingChat会话。", "llm"])
                    except BaseException as e:
                        return True, tuple([True, f"HuggingChat会话重置失败。报错原因：{str(e)}", "llm"])
            else:
                return True, tuple([True, self.help_menu(), "llm"])

        if self.curr_llm is None:
            return False, None
        

        is_react = False
        
        # print(message_obj)

        if platform == "gocq":
            if (message_obj.type == "GroupMessage" and isinstance(message_obj.message[0], At)):
                if message_obj.message[0].qq == message_obj.self_id:
                    is_react = True
            elif (message_obj.type == "FriendMessage"):
                is_react = True
        elif platform == "qqchan":
            is_react = True


        if is_react:
            if self.curr_llm == "claude":
                if self.claude_cid is None:
                    self.claude_cid = self.claude_client.create_new_chat()['uuid']
                if self.claude_client is None:
                    return True, tuple([True, "LLMS插件出现异常。（Claude未启用成功）", "llm"])
                try:
                    resp = self.claude_client.send_message(message, self.claude_cid)
                except BaseException as e:
                    return True, tuple([True, f"LLMS插件(Claude)报错：{str(e)} 会话ID: {self.claude_cid}", "llm"])
                return True, tuple([True, resp, "llm"])
            elif self.curr_llm == "huggingchat":
                if self.hc_cid is None:
                    self.hc_cid = self.hc_client.new_conversation()
                    self.hc_client.change_conversation(self.hc_cid)
                if self.hc_client is None:
                    return True, tuple([True, "LLMS插件出现异常。（HuggingChat未启用成功）", "llm"])
                try:
                    resp = self.hc_client.chat(message)
                except BaseException as e:
                    return True, tuple([True, f"LLMS插件(HuggingChat)报错：{str(e)}", "llm"])
                return True, tuple([True, resp, "llm"])
        return False, None
            
    def help_menu(self):
        return f"===大语言模型插件 V1.0===\n目前支持: \n0.不启用\n 1. Claude\n 2. HuggingChat\n\n指令：\n /llm [序号]: 切换到对应的语言模型。\n /llm reset: 重置会话\n\n当前启用的是：{self.curr_llm}"
    
    """
    帮助函数，当用户输入 plugin v 插件名称 时，会调用此函数，返回帮助信息
    返回参数要求(必填)：dict{
        "name": str, # 插件名称
        "desc": str, # 插件简短描述
        "help": str, # 插件帮助信息
        "version": str, # 插件版本
        "author": str, # 插件作者
    }
    """        
    def info(self):
        return {
            "name": "LLMSPlugin",
            "desc": "QQChannelChatGPT的大语言模型库插件：支持Claude、HuggingChat",
            "help": "测试插件, 回复helloworld即可触发",
            "version": "v1.0.1 beta",
            "author": "Soulter"
        }