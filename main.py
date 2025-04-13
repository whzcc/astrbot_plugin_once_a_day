from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import os,json,datetime
from astrbot.api.provider import ProviderRequest

@register("once_a_day", "whzc", "将某条指令设为“每个用户每天只能使用一次，第二次使用时所发消息会被修饰”，便于大模型识别", "1.0.0", "repo url")

class Main(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    # 使用插件目录下的数据文件
        plugin_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件所在目录
        self.data_file = os.path.join(plugin_dir, "history.json")

        # 初始化数据存储
        if not os.path.exists(self.data_file):
            with open(self.data_file, "w", encoding='utf-8') as f:
                f.write("{}")
                logger.info("插件 astrbot_plugin_once_a_da 已创建 history.json")


    # 注册指令的装饰器。指令名为“运势”。注册成功后，发送 `/运势` 就会触发这个指令，并将用户名写入数据
    @filter.on_llm_request()
    async def daily_luck(self, event: AstrMessageEvent, req: ProviderRequest): # 请注意有三个参数    
        # 若用户今日未使用该指令，则is_ok(sender_id)返回True，否则返回False
        '''用户每天都有一次机会通过这条指令请求llm（工作流）获得当日的运势。当用户在同一天第二次输入时，插件修改输入给llm的prompt。详见Github。'''
        def is_ok(sender_id):
            sender_id = str(sender_id)
            today = str(datetime.date.today())
            plugin_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件所在目录
            data_file = os.path.join(plugin_dir, "history.json")

            # 读取文档，如果没有“用户-日期”则写入并返回True，如果有则返回False
            with open(data_file,'r+') as f:
                read_content = json.load(f) # 读到的内容
                if sender_id in read_content:    # 如果有这个“sender_id”的键
                    if read_content[sender_id] == today:    # 值是今天
                        logger.info(f"在数据里找到了{sender_id}键，且值（请求日期）为今天，故拒绝其指令")
                        return False      
                    else:   # 值不是今天
                        logger.info(f"在数据里找到了{sender_id}键，但值（请求日期）不是今天，故同意其指令")
                        new_data = {
                        sender_id: today
                        }
                        read_content.update(new_data)
                        with open(data_file,"w") as f:
                            json.dump(read_content,f)
                        return True
                else: # 如果无这个“sender_id”的键，则向json里追加数据（使用dic的update方法）
                    logger.info(f"在数据里未找到{sender_id}键，已未其创建键值对，并同意其指令")
                    new_data = {
                        sender_id: today
                        }
                    read_content.update(new_data)
                    with open(data_file,"w") as f:
                        json.dump(read_content,f)
                    return True
        
        if req.prompt.startswith("/运势"):
            
            sender_id = event.get_sender_id()
            is_ok = is_ok(sender_id)
            logger.info(f"用户{sender_id}是否还可以请求“运势”:{is_ok}")

            if is_ok:
                return
            else:
                req.prompt = "DJAFANC3" # 用户已经不能请求运势时，将他的prompt修改为DJAFANC3
