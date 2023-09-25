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
import traceback
import asyncio

is_installed = False

try:
    from claude_api import Client
    from hugchat import hugchat
    from hugchat.login import Login
    from Bard import Chatbot as BardClient
    import anyio
    is_installed = True
except ImportError as e:
    print("===== LLMS插件依赖库未完全安装完成。请先安装或更新claude_api/hugchat/GoogleBard =====")
    # raise e

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
        self.cc.init_attributes(["llms_claude_cookie", "llms_huggingchat_email", "llms_huggingchat_psw", "llms_bard_1PSID", "llms_bard_1PSIDTS" , "llms_choice"], "")
        self.curr_llm = None
        self.claude_client = None
        self.hc_client = None
        self.claude_cid = None
        self.hc_cid = None
        self.bard_client = None
        self.bard_client_loop = None
    """
    入口函数,机器人会调用此函数。
    参数规范: message: 消息文本; role: 身份; platform: 消息平台; message_obj: 消息对象; qq_platform: QQ平台对象,可以通过调用qq_platform.send()直接发送消息。详见Helloworld插件示例
    参数详情: role为admin或者member; platform为qqchan或者gocq; message_obj为nakuru的GroupMessage对象或者FriendMessage对象或者频道的Message, DirectMessage对象。
    返回规范: bool: 是否hit到此插件(所有的消息均会调用每一个载入的插件, 如果没有hit到, 则应返回False)
             Tuple: None或者长度为3的元组。当没有hit到时, 返回None. hit到时, 第1个参数为指令是否调用成功, 第2个参数为返回的消息文本或者gocq的消息链列表, 第3个参数为指令名称
    例子: 做一个名为"yuanshen"的插件；当接收到消息为“原神 可莉”, 如果不想要处理此消息,则返回False, None；如果想要处理,但是执行失败了,返回True, tuple([False, "请求失败啦~", "yuanshen"])
          ；执行成功了,返回True, tuple([True, "结果文本", "yuanshen"])
    """
    def run(self, message: str, role: str, platform: str, message_obj, qq_platform: QQ):

        if message.lower().startswith("llm") or message.lower().startswith("/llm"):
            l = message.split(" ")
            
            if len(l) == 1:
                return True, tuple([True, self.help_menu(), "llm"])
                
            if l[1] == "0":
                self.curr_llm = None
                return True, tuple([True, "成功关闭LLMS插件,启用项目默认设置。", "llm"])
            
            # Claude -> Setting
            elif l[1] == "1":
                if is_installed == False:
                    return True, tuple([True, "LLMS插件依赖库未全部安装完成。请先安装或更新claude_api/hugchat/GoogleBard", "llm"])
                ok, p1, p2 = self.check_auth(message_obj, platform, "Claude", role)
                if not ok:
                    return p1, p2

                claude_cookie = self.cc.get("llms_claude_cookie", "")
                if claude_cookie == "":
                    return True, tuple([True, "Claude插件未被启用。因为您未填写claude的cookie,请机器人管理员先私聊机器人发送\n\n/llm claude [您在Claude上的的Cookie]\n\n以激活。(或者在cmd_config文件内修改)", "llm"])
                try:
                    self.claude_client = Client(claude_cookie)
                    self.claude_cid = self.claude_client.create_new_chat()['uuid']
                    self.curr_llm = "claude"
                    return True, tuple([True, "成功启用LLMS插件,启用Claude模型,将在下次回答生效！", "llm"])
                except BaseException as e:
                    return True, tuple([True, f"Claude插件未被启用。可能因为您的Claude的Cookie不正确。\n\n报错堆栈: {traceback.format_exc()}", "llm"])
            
            # HuggingChat -> Setting
            elif l[1] == "2":
                if is_installed == False:
                    return True, tuple([True, "LLMS插件依赖库未全部安装完成。请先安装或更新claude_api/hugchat/GoogleBard", "llm"])
                ok, p1, p2 = self.check_auth(message_obj, platform, "HuggingChat", role)
                if not ok:
                    return p1, p2
                
                email = self.cc.get("llms_huggingchat_email", "")
                psw = self.cc.get("llms_huggingchat_psw", "")
                if email == "" or psw == "":
                    return True, tuple([True, "HuggingChat插件未被启用。因为您未填写HuggingChat的账号,请机器人管理员先私聊机器人发送\n\n/llm hc [您的邮箱] [您的密码]\n\n以激活。(或者在cmd_config文件内修改)", "llm"])
                try:
                    sign = Login(email, psw)
                    cookies = sign.login()
                    cookie_path_dir = "./llms_huggingchat_cookies"
                    sign.saveCookiesToDir(cookie_path_dir)
                    self.hc_client = hugchat.ChatBot(cookies=cookies.get_dict())
                    self.hc_cid = self.hc_client.new_conversation()
                    self.hc_client.change_conversation(self.hc_cid)
                    self.curr_llm = "huggingchat"
                    return True, tuple([True, "成功启用LLMS插件,启用HuggingChat模型,将在下次回答生效！", "llm"])
                except BaseException as e:
                    return True, tuple([True, f"HuggingChat插件未被启用。可能因为您的HuggingChat的账号不正确。\n\n报错堆栈: {traceback.format_exc()}", "llm"])
                
            elif l[1] == "3":
                if is_installed == False:
                    return True, tuple([True, "LLMS插件依赖库未全部安装完成。请先安装或更新claude_api/hugchat/GoogleBard", "llm"])
                ok, p1, p2 = self.check_auth(message_obj, platform, "Google Bard", role)
                if not ok:
                    return p1, p2
                try:
                    Secure_1PSID = self.cc.get("llms_bard_1PSID", "")
                    Secure_1PAPISID = self.cc.get("llms_bard_1PAPISID", "")
                    if Secure_1PSID == "" or Secure_1PAPISID == "":
                        return True, tuple([True, "Bard插件未被启用: 您未填写Bard的1PSID和1PAPISID,请机器人管理员先私聊机器人发送\n\n/llm bard [您的1PSID] [您的1PAPISID]\n\n以激活。(或者在cmd_config文件内修改)", "llm"])
                    self.bard_client_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(self.bard_client_loop)
                    self.bard_client = BardClient(Secure_1PSID, Secure_1PAPISID)

                    # self.bard_client = self.start_bard(Secure_1PSID, Secure_1PAPISID)
                    # self.bard_client = asyncio.run(self.start_bard(Secure_1PSID, Secure_1PAPISID))
                    # future = asyncio.run_coroutine_threadsafe(self.start_bard(Secure_1PSID, Secure_1PAPISID), self.bard_client_loop)
                    # self.bard_client = future.result()
                    self.curr_llm = "bard"
                    return True, tuple([True, "成功启用LLMS插件, 启用Bard模型,将在下次回答生效！", "llm"])
                except TimeoutError as e:
                    return True, tuple([True, "Bard插件未被启用: 连接超时，可能是代理的原因。", "llm"])
                except BaseException as e:
                    return True, tuple([True, f"Bard插件未被启用: 未知错误。\n\n报错堆栈: {traceback.format_exc()}", "llm"])

            elif l[1] == "claude" and len(l) >= 3:
                ok, p1, p2 = self.check_auth(message_obj, platform, "Claude", role)
                if not ok:
                    return p1, p2
                
                cookies_str = "".join(l[2:])
                self.cc.put("llms_claude_cookie", cookies_str)
                return True, tuple([True, "成功设置Claude的Cookie, 您现在可以启用Claude了。", "llm"])
            elif l[1] == "hc" and len(l) == 4:
                ok, p1, p2 = self.check_auth(message_obj, platform, "HuggingChat", role)
                if not ok:
                    return p1, p2
                email = l[2]
                psw = l[3]
                self.cc.put("llms_huggingchat_email", email)
                self.cc.put("llms_huggingchat_psw", psw)
                return True, tuple([True, "成功设置HuggingChat的账号, 您现在可以启用HuggingChat了。", "llm"])
            elif l[1] == "bard" and len(l) == 4:
                ok, p1, p2 = self.check_auth(message_obj, platform, "Google Bard", role)
                if not ok:
                    return p1, p2
                Secure_1PSID = l[2]
                Secure_1PAPISID = l[3]
                self.cc.put("llms_bard_1PSID", Secure_1PSID)
                self.cc.put("llms_bard_1PAPISID", Secure_1PAPISID)
                return True, tuple([True, "成功设置Bard的账号, 您现在可以启用Bard了。", "llm"])
            
            elif l[1] == "reset":
                if self.curr_llm == "claude":
                    try:
                        self.claude_cid = self.claude_client.create_new_chat()['uuid']
                        return True, tuple([True, "成功重置Claude会话。", "llm"])
                    except BaseException as e:
                        return True, tuple([True, f"Claude会话重置失败。报错原因: {str(e)}", "llm"])
                    
                elif self.curr_llm == "huggingchat":
                    try:
                        self.hc_cid = self.hc_client.new_conversation()
                        self.hc_client.change_conversation(self.hc_cid)
                        return True, tuple([True, "成功重置HuggingChat会话。", "llm"])
                    except BaseException as e:
                        return True, tuple([True, f"HuggingChat会话重置失败。报错原因: {str(e)}", "llm"])
                elif self.curr_llm == "bard":
                    return True, tuple([True, f"暂时不支持重置Bard的对话。", "llm"])
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
                    return True, tuple([True, f"LLMS插件(Claude)报错: {str(e)} 会话ID: {self.claude_cid}", "llm"])
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
                    return True, tuple([True, f"LLMS插件(HuggingChat)报错: {str(e)}", "llm"])
                return True, tuple([True, resp, "llm"])
            elif self.curr_llm == "bard":
                if self.bard_client is None:
                    return True, tuple([True, "LLMS插件出现异常。（Claude未启用成功）", "llm"])
                
                while True:
                    try:
                        resp = self.bard_client.ask(message)
                        break
                    except BaseException as e:
                        if "SNlM0e value not found in response. Check __Secure_1PSID value." in str(e):
                            return True, tuple([True, "LLMS插件: Bard会话已过期, 请重新设置1PSID、1PSIDTS字段。", "llm"])
                        elif "This event loop is already running" in str(e):
                            time.sleep(2)
                        else:
                            return True, tuple([True, f"LLMS插件(Bard)报错: {str(e)}", "llm"])
                return True, tuple([True, resp['content'], "llm"])

        return False, None
            
    def help_menu(self):
        return f"===大语言模型插件 V1.0===\n目前支持: \n0. 不启用\n1. Claude\n2. HuggingChat\n3. Google Bard\n指令: \n /llm [序号]: 切换到对应的语言模型。\n /llm reset: 重置会话\n\n当前启用的是: {self.curr_llm}"
    
    async def start_bard(self, Secure_1PSID, Secure_1PAPISID):
        return BardClient(Secure_1PSID, Secure_1PAPISID)

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
            "name": "LLMSPlugin",
            "desc": "QQChannelChatGPT的大语言模型库插件: 支持Claude、HuggingChat、Google Bard",
            "help": "前往https://github.com/Soulter/llms查看帮助",
            "version": "v1.0.2",
            "author": "Soulter"
        }
