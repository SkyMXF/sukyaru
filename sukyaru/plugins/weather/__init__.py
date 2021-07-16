import time

import nonebot
from nonebot import on_command, get_driver
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.log import logger

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .config import Config
from .data_source import get_day_weather, gen_weather_msg

global_config = get_driver().config
weather_config = Config(**global_config.dict())

scheduler = AsyncIOScheduler()
if not scheduler.running:
    scheduler.configure(weather_config.apscheduler_config)
    scheduler.start()
    logger.opt(colors=True).info("<y>Scheduler Started</y>")

# scheduler weather report
@scheduler.scheduled_job('cron', hour='7', minute='00', second='0')
async def weather_report():
    bots = nonebot.get_bots()
    cities_dict = weather_config.weather_report_cities
    for bot_id, bot in bots.items():
        for group_id in cities_dict.keys():
            for city_name in cities_dict[group_id]:
                city_weather = get_day_weather(
                    key=weather_config.qweather_key,
                    location=city_name,
                    only_one=True
                )
                if city_weather["code"]:
                    msg = gen_weather_msg(city_weather["result"], use_prefix=True)
                    await bot.send_msg(group_id=int(group_id), message=msg)
                time.sleep(1)

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
            msg = gen_weather_msg(city_weather["result"], use_prefix=False)
            await weather.finish(msg)
        else:
            await weather.finish("暂时无法查询'%s'的天气"%(args))
    else:
        await weather.finish("天气功能未实装")
