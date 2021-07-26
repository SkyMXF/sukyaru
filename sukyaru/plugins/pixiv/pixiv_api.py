import pixivpy3 as pixiv
import time
import random

from .model import save_illu_info

def get_api_obj(refresh_token=None, proxy_port=None):

    params = {}
    if not (proxy_port is None):
        params["proxies"] = {
            "https": "http://127.0.0.1:%d"%(proxy_port)
        }
    api = pixiv.AppPixivAPI(**params)
    #api.set_api_proxy("http://app-api.pixivlite.com")

    if not (refresh_token is None):
        api.auth(refresh_token=refresh_token)
    
    return api

def update_db(refresh_token, wait_time=5, logger=None, proxy_port=None):
    if not (logger is None):
        logger.opt(colors=True).info("<y>[PIXIV UPDATE DB]Begin to update pixiv db</y>")

    api = get_api_obj(refresh_token, proxy_port)

    total_update = 0

    update_num = 0
    json_result = api.illust_follow()
    for illust in json_result.illusts:
        try:
            update_num += save_illu_info(int(illust.id), illust.title, illust.user.name, illust.image_urls.medium)
        except:
            if not (logger is None):
                logger.opt(colors=True).info("<y>[PIXIV UPDATE DB]Encounter an exception with (%d, %s, %s, %s)</y>"%(
                    int(illust.id), illust.title, illust.user.name, illust.image_urls.medium
                ))
    total_update += update_num
    if not (logger is None):
        if update_num > 0:
            logger.opt(colors=True).info("<y>[PIXIV UPDATE DB]update %d from %d illust</y>"%(update_num, len(json_result.illusts)))
    
    while True:
        time.sleep(wait_time + random.randint(-1, 1))
        next_qs = api.parse_qs(json_result.next_url)
        if next_qs is None:
            break
        json_result = api.illust_follow(**next_qs)
        update_num = 0
        for illust in json_result.illusts:
            try:
                update_num += save_illu_info(int(illust.id), illust.title, illust.user.name, illust.image_urls.medium)
            except:
                if not (logger is None):
                    logger.opt(colors=True).info("<y>[PIXIV UPDATE DB]Encounter an exception with (%d, %s, %s, %s)</y>"%(
                        int(illust.id), illust.title, illust.user.name, illust.image_urls.medium
                    ))
        total_update += update_num
        if not (logger is None):
            if update_num > 0:
                logger.opt(colors=True).info("<y>[PIXIV UPDATE DB]update %d from %d illust</y>"%(update_num, len(json_result.illusts)))
    
    if not (logger is None):
        logger.opt(colors=True).info("<y>[PIXIV UPDATE DB]Totally update %d illust</y>"%(total_update))
    