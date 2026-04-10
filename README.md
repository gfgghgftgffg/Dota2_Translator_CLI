# Dota 2 Translator CLI

这是一个纯命令行的 Dota 2 聊天翻译器，主要代码从[Dota2_Translator_GUI](https://github.com/dyygs/Dota2_Translator_GUI)fork来。

考虑到翻译的实时性，以及原来的prompt写的并不是很好，所以我把翻译功能抽离出来，做成了一个独立的 CLI 程序方便自己使用。

欢迎大家来提更多的few shot prompt和词汇表更新。

程序流程：
1. 监听全局热键
2. 复制当前输入框内容
3. 先用本地 Dota 术语词库替换并保护关键术语
4. 调用本地 Ollama 的 POST 接口翻译
5. 将译文粘贴回输入框（并发送）

<video controls width="640" height="360">
  <source src="./example.mp4" type="video/mp4">
  你的浏览器不支持视频标签。
</video>

## 运行

1.conda配置一下
2.新建一个config.json,需要的自行修改
```
{
  "hotkeys": {
    "trigger": "f12",
    "toggle": "ctrl+alt+f12"
  },
  "translation": {
    "cooldown": 0.2,
    "source_lang": "zh-CN",
    "target_lang": "en",
    "mode": 1
  },
  "window_filter": {
    "enabled": false,
    "title_keywords": [
      "dota 2"
    ]
  },
  "ollama": {
    "host": "10.244.0.2",
    "port": 11434,
    "endpoint": "/api/generate",
    "model": "qwen3.5:4b",
    "timeout": 30,
    "think": false,
    "options": {
      "temperature": 0.8
    }
  },
  "prompt": {
    "file": "prompts/zh_to_en_prompt.txt",
    "user_text_placeholder": "{{text}}"
  }
}

```

## 配置文件

运行参数都放在外部配置文件(.\config.json)里：

- 热键
- 翻译冷却时间
- 是否只在 Dota 2 窗口中触发
- Ollama 的 IP、端口、接口路径、模型名、超时和推理参数
- Prompt 文件路径


## 词汇表格式

词汇表文件在 [`src/词汇表.py`](.\src\词汇表.py)。
现在采用每行一个条目的可编辑格式：

```text
羊刀:hex
肉山:roshan
抓人:gank
```

程序会在翻译前把命中的条目替换成：

```text
<dota2word>hex</dota2word>
```

## Prompt 文件

Ollama 请求中的提示词已经拆到独立文件，默认是：

[`prompts/zh_to_en_prompt.txt`](.\prompts\zh_to_en_prompt.txt)

这个文件支持直接写 few-shot。程序会把用户待翻译文本填入 `{{text}}` 占位符，然后整体作为 `prompt` 发给 Ollama。
