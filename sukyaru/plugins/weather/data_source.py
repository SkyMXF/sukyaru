import httpx
import random

success_code = "200"
timeout = httpx.Timeout(3, read=2)

def get_day_weather(key: str, location: str, only_one=False):

    city_list = get_city_list(key, location)
    if city_list["code"] != success_code:
        return {"code": False}
    city_list = city_list["cities"]
    if len(city_list) == 0:
        return {"code": False}
    
    weather_list = []
    for city_info in city_list:
        weather_params = {"key": key, "location": city_info["id"]}
        
        weather_result = httpx.get(
            'https://devapi.qweather.com/v7/weather/3d',
            params=weather_params,
            timeout=timeout
        ).json()
        
        if weather_result["code"] != success_code:
            return {"code": False}
        
        day_weather = weather_result["daily"][0]
        day_weather = {
            "city": city_info["name"],
            "adm": city_info["adm1"],
            "tempMin": day_weather["tempMin"],
            "tempMax": day_weather["tempMax"],
            "textDay": day_weather["textDay"],
            "textNight": day_weather["textNight"],
            "windDirDay": day_weather["windDirDay"],
            "windScaleDay": day_weather["windScaleDay"],
            "windDirNight": day_weather["windDirNight"],
            "windScaleNight": day_weather["windScaleNight"],
            "uvIndex": day_weather["uvIndex"],
        }

        if only_one:
            return {"code": True, "result": day_weather}

        weather_list.append(day_weather)

    return {"code": True, "result": weather_list}

def get_city_list(key: str, location: str):

    geo_params = {"key": key, "location": location}
    search_result = httpx.get(
        'https://geoapi.qweather.com/v2/city/lookup',
        params=geo_params,
        timeout=timeout
    ).json()
    if search_result["code"] != success_code:
        return {"code": search_result["code"]}

    # get_id
    city_list = []
    for city_dict in search_result["location"]:
        if city_dict["name"] in location:
            city_list.append({"name": city_dict["name"], "adm1": city_dict["adm1"], "id": city_dict["id"]})
    
    return {"code": search_result["code"], "cities": city_list}

msg_prefix_list = ["爷来哩！", "呵欠————好几把早。", "早安。", "大家好，", "嘤 ", "都给爷起来，"]
def gen_weather_msg(one_city_weather, use_prefix=False):
    """
    day_weather.keys() = [
        "city", "adm",
        "tempMin", "tempMax",
        "textDay", "textNight",
        "windDirDay", "windScaleDay",
        "windDirNight", "windScaleNight",
        "uvIndex"
    ]
    """

    warning_msg = ""

    # wind level check
    wind_levels = one_city_weather["windScaleDay"].split("-") + one_city_weather["windScaleNight"].split("-")
    wind_levels = [int(wl) for wl in wind_levels]
    min_wl = min(*wind_levels)
    max_wl = max(*wind_levels)

    # uv check
    uv_level = int(one_city_weather["uvIndex"])

    # temp check
    max_temp = int(one_city_weather["tempMax"])
    min_temp = int(one_city_weather["tempMin"])

    if min_wl >= 7:
        # strong wind
        warning_msg = "风贼几把大"
    elif ("雨" in one_city_weather["textDay"]) or ("雨" in one_city_weather["textNight"]) or ("雪" in one_city_weather["textDay"]) or ("雪" in one_city_weather["textNight"]):
        # rain or snow
        warning_msg = "记得带伞哩"
    elif min_wl >= 5:
        # weak wind
        warning_msg = "风会有点点大"
    elif uv_level >= 8:
        warning_msg = "干，今天晒太阳会烧伤"
    elif uv_level >= 6:
        warning_msg = "在户外需要高强度防晒"
    elif uv_level >= 3:
        warning_msg = "需要小防晒一下"
    elif max_temp - min_temp >= 13:
        warning_msg = "今天昼夜温差贼几把大"
    elif max_temp >= 35:
        warning_msg = "干，好热"
    elif min_temp <= 0:
        warning_msg = "草，冻死爷了"
    else:
        warning_msg = "今天会是个好天气（迫真"
    
    if one_city_weather["textDay"] == one_city_weather["textNight"]:
        weather_type = one_city_weather["textDay"]
    else:
        weather_type = "%s转%s"%(one_city_weather["textDay"], one_city_weather["textNight"])
    if one_city_weather["windDirDay"] == one_city_weather["windDirNight"]:
        wind_msg = "%s%d-%d级"%(one_city_weather["windDirDay"], min_wl, max_wl)
    else:
        wind_msg = "%s%s级转%s%s级"%(
            one_city_weather["windDirDay"], one_city_weather["windScaleDay"],
            one_city_weather["windDirNight"], one_city_weather["windScaleNight"]
        )
    
    weather_msg = "%s今天%s，%s-%s°C，%s，紫外线指数%s。%s"%(
        one_city_weather["city"], weather_type, one_city_weather["tempMin"], one_city_weather["tempMax"], wind_msg, one_city_weather["uvIndex"], warning_msg
    )

    return weather_msg