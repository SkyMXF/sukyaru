import nonebot
from nonebot import on_command, get_driver, on_regex
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.log import logger

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .config import Config

global_config = get_driver().config
repeater_config = Config(**global_config.dict())

repeater = on_regex(".*", priority=99)

msg_windows = dict()

@repeater.handle()
async def follow_repeater(bot: Bot, event: Event, state: T_State):

    # check serving group
    sess_id = event.get_session_id()
    
    if "group" in sess_id:
        group_id = sess_id[sess_id.index("_") + 1 : sess_id.rindex("_")]
        if not (group_id in repeater_config.serving_group):
            return
        
        global msg_windows
        if not (group_id in msg_windows.keys()):
            msg_windows[group_id] = ["" for _ in range(repeater_config.msg_window_len)]
    else:
        # only for group chat
        return

    # append new msg to window
    msg = str(event.get_message())
    msg_windows[group_id] = msg_windows[group_id][1:] + [msg]

    # check repeating times
    checking_dict = dict()
    repeating_msg = None
    for msg in msg_windows[group_id]:
        # counting
        if len(msg) == 0:
            continue
        if not (msg in checking_dict.keys()):
            checking_dict[msg] = 1
        else:
            checking_dict[msg] += 1
            if checking_dict[msg] >= repeater_config.trigger_msg_times:
                repeating_msg = msg
    if not (repeating_msg is None):
        for idx_in_win in range(len(msg_windows[group_id])):
            if msg_windows[group_id][idx_in_win] == repeating_msg:
                msg_windows[group_id][idx_in_win] = ""
        await repeater.finish(repeating_msg)
    
