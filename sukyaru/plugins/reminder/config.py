from pydantic import Field, BaseSettings


class Config(BaseSettings):
    server_host = ""
    remind_server_port = 80
    apscheduler_config: dict = Field(
        default_factory=lambda: {"apscheduler.timezone": "Asia/Shanghai"})

    class Config:
        extra = "ignore"