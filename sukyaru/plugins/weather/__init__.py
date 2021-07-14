from nonebot import on_command, get_driver
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.log import logger

from .config import Config
from .data_source import get_day_weather, gen_weather_msg

global_config = get_driver().config
weather_config = Config(**global_config.dict())

weather = on_command("天气", priority=5)

@weather.handle()
async def day_weather(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()

    # check serving group
    sess_id = event.get_session_id()
    
    if "group" in sess_id:
        group_id = sess_id[sess_id.index("_") + 1 : sess_id.rindex("_")]
        if not (group_id in weather_config.serving_group):
            return

    if len(args) == 0:
        args = "上海"
    if len(weather_config.qweather_key) > 0:
        city_weather = get_day_weather(
            key=weather_config.qweather_key,
            location=args,
            only_one=True
        )
        #logger.log("INFO", str(type(response)) + " " + str(response))
        if city_weather["code"]:
            print("sending...")
            await weather.finish(gen_weather_msg(city_weather["result"], use_prefix=True))
        else:
            await weather.finish("暂时无法查询'%s'的天气"%(args))
    else:
        await weather.finish("天气功能未实装")

"""
@weather.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()  # 首次发送命令时跟随的参数，例：/天气 上海，则args为上海
    if args:
        state["city"] = args  # 如果用户发送了参数则直接赋值

@weather.got("city", prompt="你想查询哪个城市的天气呢？")
async def handle_city(bot: Bot, event: Event, state: T_State):
    city = state["city"]
    if city not in ["上海", "北京"]:
        await weather.reject("你想查询的城市暂不支持，请重新输入！")
    city_weather = await get_weather(city)
    await weather.finish(city_weather)


async def get_weather(city: str):
    return f"{city}的天气是..."
"""