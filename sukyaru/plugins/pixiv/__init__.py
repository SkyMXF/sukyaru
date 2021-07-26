import re
import os
import time
import asyncio
import datetime
import nonebot
from nonebot import init, on_command, get_driver, on_regex
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.log import logger

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger

from .config import Config
from .model import init_db, get_n_illu
from .pixiv_api import get_api_obj, update_db

global_config = get_driver().config
pixiv_config = Config(**global_config.dict())
if pixiv_config.proxy_port == 0:
    pixiv_config.proxy_port = None

init_db()
scheduler = BackgroundScheduler()
if not scheduler.running:
    scheduler.configure(pixiv_config.apscheduler_config)
    scheduler.start()

pixiv_cmd = on_command("色图", aliases={"涩图", "来波车"}, priority=5)
@pixiv_cmd.handle()
async def car_on(bot: Bot, event: Event, state: T_State):
    # dont send in private
    sess_id = event.get_session_id()
    if not ("group" in sess_id):
        return
    group_id = sess_id[sess_id.index("_") + 1 : sess_id.rindex("_")]
    if not (group_id in pixiv_config.serving_group):
        return
    
    # get illu number
    args = str(event.get_message())
    args = args.strip()
    require_num = pixiv_config.illu_default_num
    if len(args) > 0:
        try:
            require_num = int(args)
        except:
            require_num = pixiv_config.illu_default_num
    
    if require_num < 1:
        require_num = 1
    if require_num > pixiv_config.illu_max_num:
        require_num = pixiv_config.illu_max_num

    # get random illu url
    illu_list = await get_n_illu(require_num)
    if len(illu_list) == 0:
        await pixiv_cmd.finish("车车油不足哩")
        return

    # download and send
    try:
        api = get_api_obj(proxy_port=pixiv_config.proxy_port)
        if not os.path.exists(pixiv_config.illu_tmp_dir):
            os.makedirs(pixiv_config.illu_tmp_dir)
        for illu_info in illu_list:
            api.download(illu_info["url"], path=pixiv_config.illu_tmp_dir, name="car_on.jpg")
            tmp_save_path = os.path.join(pixiv_config.illu_tmp_dir, "car_on.jpg")
            await bot.send_msg(
                group_id=group_id,
                message="[CQ:image,file=file://%s]\n画师: %s, 标题: %s"%(
                    tmp_save_path, illu_info["author"], illu_info["title"]
                )
            )
            os.remove(tmp_save_path)
            time.sleep(2)
    except Exception as e:
        print(e)
        await pixiv_cmd.finish("干，发动机坏了")
        return

# scheduler pixiv upate
@scheduler.scheduled_job('cron', hour='4', minute='5', second='0')
def scheduled_update_pixiv_db():
    update_db(pixiv_config.pixiv_refresh_token, logger=logger, proxy_port=pixiv_config.proxy_port)

delta_time = datetime.timedelta(seconds=5)
trigger = DateTrigger(run_date=datetime.datetime.now() + delta_time)
scheduler.add_job(
    update_db,
    trigger=trigger,
    args=[pixiv_config.pixiv_refresh_token, 5, logger, pixiv_config.proxy_port]
)