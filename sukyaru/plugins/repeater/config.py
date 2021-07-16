from pydantic import Field, BaseSettings


class Config(BaseSettings):
    serving_group: list = []
    msg_window_len: int = 5
    trigger_msg_times: int = 2

    class Config:
        extra = "ignore"