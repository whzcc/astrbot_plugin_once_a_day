from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import sqlite3
from datetime import datetime

# 数据库部分开始
# 连接到SQLite数据库（如果数据库不存在，则会自动创建）
conn = sqlite3.connect('once_a_day.db')
cursor = conn.cursor()
# 创建表来存储用户输入的字符串和日期
cursor.execute('''
CREATE TABLE IF NOT EXISTS inputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    input_text TEXT NOT NULL,
    input_date DATE NOT NULL,
    UNIQUE(input_text, input_date)
)
''')
conn.commit()
        
def is_input_allowed(input_text):
    # 获取当前日期
    today = datetime.now().date()
    
    # 检查是否已经存在相同的输入和日期
    cursor.execute('''
    SELECT 1 FROM inputs WHERE input_text = ? AND input_date = ?
    ''', (input_text, today))
    
    # 如果查询结果不为空，说明已经输入过
    if cursor.fetchone():
        return False
    else:
        return True

def save_input(input_text):
    # 获取当前日期
    today = datetime.now().date()
    
    # 将输入和日期插入到数据库中
    cursor.execute('''
    INSERT INTO inputs (input_text, input_date) VALUES (?, ?)
    ''', (input_text, today))
    conn.commit()

def is_ok(requester_name):
    if is_input_allowed(requester_name):
        save_input(requester_name)
        # conn.close() # 关闭数据库连接
        return True
    else:
        # conn.close()
        return False

@register("once-a-day", "whzc", "将某条指令设为“每个用户每天只能使用一次，第二次使用时所发消息会被修饰”，便于大模型识别", "1.0.0", "repo url")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
    # 注册指令的装饰器。指令名为“运势”。注册成功后，发送 `/运势` 就会触发这个指令，并将用户名写入数据库`
    @filter.command("运势")
    async def once_a_day(self, event: AstrMessageEvent):
        '''用户输入这个指令时，他的名字会被写入数据库''' # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str # 用户发的纯文本消息字符串
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        
        # 若用户今日未使用该指令，则is_ok(user_name)返回True，否则返回False
        is_ok = is_input_allowed(user_name)
        if is_ok:
            yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!") # 发送一条纯文本消息
        else:
            yield event.plain_result(f"No!, {user_name}, 你发了 {message_str}!") # 发送一条纯文本消息

        logger.info(message_chain)
