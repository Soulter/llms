# LLMS Plugin For AstrBot

AstrBot（原 QQChannelChatGPT）接入更多大语言模型的插件。

# 支持：
1. [Claude](https://github.com/KoushikNavuluri/Claude-API)
2. [HuggingChat](https://github.com/Soulter/hugging-chat-api)
3. [Google Gemini](https://makersuite.google.com/app/apikey)
4. New Bing

## 计划支持

> 欢迎任何贡献！❤️

暂无

# 使用方法

在聊天区发送 `plugin i https://github.com/Soulter/llms` 或者在可视化面板安装插件。

安装成功后，请在可视化面板配置插件。

<img width="500" alt="image" src="https://github.com/Soulter/llms/assets/37870767/68ddd361-d6d2-43b9-b01e-d236d072f4d9">

配置完成后，在聊天区输入 `provider` 指令即可查看启用的 LLM 资源。


# 注意事项
需要更新 AstrBot 到 v3.1.4 版本（2024/02/07之后的）。

Claude 模型的 Cookie 的获取方式请见： https://github.com/KoushikNavuluri/Claude-API 

HuggingChat 需要先免费注册一个 HuggingFace 账号：https://huggingface.co

Gemini API Key 申请链接（目前免费）： https://makersuite.google.com/app/apikey

使用 Newbing 需要复制 cookies (450行+) 到 `data/newbing_cookies.json`
