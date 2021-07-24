import re
import time
import asyncio
import datetime
import nonebot
from nonebot import on_command, get_driver, on_regex
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.log import logger

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from .config import Config
from .model import init_db, save_reminds, read_reminds, remove_remind

global_config = get_driver().config
reminder_config = Config(**global_config.dict())

# init
init_db()
scheduler = AsyncIOScheduler()
if not scheduler.running:
    scheduler.configure(reminder_config.apscheduler_config)
    scheduler.start()

set_reminder = on_command("定时", aliases={"闹钟", "计时"}, rule=to_me(), priority=5)
@set_reminder.handle()
async def add_remind(bot: Bot, event: Event, state: T_State):
    # dont send in group
    sess_id = event.get_session_id()
    if "group" in sess_id:
        return

    args = str(event.get_message())
    args = args.strip()

    if len(args) == 0:
        await set_reminder.finish("设置定时需要这样的格式噢：'定时 0.45.23 打胖胖'，这样就设置了0小时45分钟23秒后打胖胖哩")
        return

    arg_re = re.compile(r"^(?P<hour>\d+)(?:\.(?P<minute>\d+))?(?:\.(?P<second>\d+))?(?:\s+(?P<text>.*))?$")
    match_args = re.search(arg_re, args)
    if match_args:
        set_hour = int(match_args.group("hour")) if match_args.group("hour") else 0
        set_min = int(match_args.group("minute")) if match_args.group("minute") else 0
        set_sec = int(match_args.group("second")) if match_args.group("second") else 0
        set_text = match_args.group("text") if match_args.group("text") else ""
    else:
        await set_reminder.finish("设置定时需要这样的格式噢：'定时 0.45.23 打胖胖'，这样就设置了0小时45分钟23秒后打胖胖哩")
        return

    user_qq = int(event.get_user_id())
    delta_time = set_hour * 3600.0 + set_min * 60.0 + set_sec
    remind_time = time.time() + delta_time
    text = set_text

    save_row_id = await save_reminds(user_qq, remind_time, text)
    
    add_sched(
        rowid=save_row_id,
        user_qq=user_qq,
        delta_time=delta_time,
        text=set_text
    )
    msg = "好哩~凯露酱会在%d小时%d分钟%d秒后提醒你"%(set_hour, set_min, set_sec)
    end_msg = "~" if len(text) == 0 else "'%s'"%(text)
    await set_reminder.finish(msg + end_msg)

async def send_remind(user_qq: int, rowid: int, text: str, remind_type="normal"):

    if remind_type == "past":
        msg = "嘤嘤抱歉~因为服务器重启等原因，你设置的闹钟晚来了一点点噢"
    else:
        msg = "喵喵~你设置的闹钟响哩"
    if len(text) > 0:
        msg += "，内容是'%s'"%(text)
    
    bots = nonebot.get_bots()
    for bot_id, bot in bots.items():
        await bot.send_msg(user_id=user_qq, message=msg)
    
    await remove_remind(rowid)

async def check_unsend():

    remind_list = await read_reminds()
    logger.opt(colors=True).info("<y>Got %d unsend reminds</y>"%(len(remind_list)))
    for remi in remind_list:
        if time.time() + 10.0 > remi["time"]:
            # past alarm
            await send_remind(
                user_qq=remi["qq"],
                rowid=remi["rowid"],
                text=remi["text"],
                remind_type="past"
            )
        else:
            add_sched(
                rowid=remi["rowid"],
                user_qq=remi["qq"],
                delta_time=remi["time"] - time.time(),
                text=remi["text"]
            )

delta_time = datetime.timedelta(seconds=5)
trigger = DateTrigger(run_date=datetime.datetime.now() + delta_time)
scheduler.add_job(
    check_unsend,
    trigger=trigger
)

def add_sched(rowid:int, user_qq:int, delta_time:float, text:str):

    delta_time = datetime.timedelta(seconds=delta_time)
    trigger = DateTrigger(run_date=datetime.datetime.now() + delta_time)
    scheduler.add_job(
        send_remind,
        trigger=trigger,
        args=[user_qq, rowid, text]
    )

    time.sleep(1)


