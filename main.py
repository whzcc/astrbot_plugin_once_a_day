from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import os,json
from datetime import datetime

@register("once-a-day", "whzc", "将某条指令设为“每个用户每天只能使用一次，第二次使用时所发消息会被修饰”，便于大模型识别", "1.0.0", "repo url")
class Main(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    # 使用插件目录下的数据文件
        plugin_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件所在目录
        self.data_file = os.path.join(plugin_dir, "query_history.json")
        
        # 初始化数据存储
        if not os.path.exists(self.data_file):
            with open(self.data_file, "w", encoding='utf-8') as f:
                f.write("{}")
        with open(self.data_file, "r", encoding='utf-8') as f:
            self.memories = json.load(f)
            logger.info("query_history.json is created")

    # 注册指令的装饰器。指令名为“运势”。注册成功后，发送 `/运势` 就会触发这个指令，并将用户名写入数据
    @filter.command("运势")
    async def once_a_day(self, event: AstrMessageEvent):
        '''用户输入这个指令时，他的名字会被写入数据库''' # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        
        sender_id = event.get_sender_id()
        message_str = event.message_str # 用户发的纯文本消息字符串
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        
        # 若用户今日未使用该指令，则is_ok(sender_id)返回True，否则返回False
        is_ok = True
        logger.info(f"用户{sender_id}是否还可以请求“运势”:{is_ok}")
        if is_ok:
            yield event.plain_result(f"Hello, {sender_id}, 你发了 {message_str}!") # 发送一条纯文本消息
        else:
            yield event.plain_result(f"No!, {sender_id}, 你发了 {message_str}!") # 发送一条纯文本消息

        logger.info(message_chain)
