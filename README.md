# Dota 2 Translator CLI

这是一个纯命令行的 Dota 2 聊天翻译器，主要代码从[Dota2_Translator_GUI](https://github.com/dyygs/Dota2_Translator_GUI)fork来。

考虑到翻译的实时性，以及原来的prompt写的并不是很好，所以我把翻译功能抽离出来，做成了一个独立的 CLI 程序方便自己使用。

欢迎大家来提更多的few shot prompt和词汇表更新，很多东西必须打了才知道原来不支持（比如刚发现吃兵这个词不在词汇表里）。

程序流程：
1. 监听全局热键
2. 复制当前输入框内容
3. 先用本地 Dota 术语词库替换并保护关键术语
4. 调用本地 Ollama 的 POST 接口翻译
5. 将译文粘贴回输入框（并发送）

![example](example.gif)

## 更新

- 2026-04-22：新增了对llamacpp的支持（因为我想提速），配置文件里可以选择使用ollama还是llamacpp了。（但是目前有bug，尤其是对qwen这种能开关思考的模型，完全没做适配，有需求的自行适配或者找我merge吧，源代码给了一个qwen3.6适配的例子。而且很奇怪非ollama的gemma4-e4b似乎是能力不大行，有时候不按prompt要求来生成，反正目前用起来感觉没ollama省心） 感觉还是切回ollama那个gemma4模型比较好。



## 运行

1.conda配置一下

2.修改config.json

3. python src\dota2_translator.py

## 配置文件

运行参数都放在外部配置文件(.\config.json)里：

- 热键
- 翻译冷却时间
- 是否只在 Dota 2 窗口中触发
- Ollama 的 IP、端口、接口路径、模型名、超时和推理参数
- Prompt 文件路径


## 模型推荐
不要使用qwen等国产模型，因为不翻译脏话，任何脏话都会使得输出变奇怪。

建议使用gemma，模型不需要参数量大，目前感觉prompt设计得好才是关键，4b即可。


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
