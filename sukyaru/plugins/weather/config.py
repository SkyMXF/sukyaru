from pydantic import BaseSettings


class Config(BaseSettings):
    qweather_key: str = ""
    serving_group: list = []

    class Config:
        extra = "ignore"