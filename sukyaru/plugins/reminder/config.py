from pydantic import Field, BaseSettings


class Config(BaseSettings):
    apscheduler_config: dict = Field(
        default_factory=lambda: {"apscheduler.timezone": "Asia/Shanghai"})

    class Config:
        extra = "ignore"