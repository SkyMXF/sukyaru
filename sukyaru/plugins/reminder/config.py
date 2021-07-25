from pydantic import Field, BaseSettings


class Config(BaseSettings):
    server_host = "http://skymxf.asia"
    remind_server_port = 43967
    apscheduler_config: dict = Field(
        default_factory=lambda: {"apscheduler.timezone": "Asia/Shanghai"})

    class Config:
        extra = "ignore"