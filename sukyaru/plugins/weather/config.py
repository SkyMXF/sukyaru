from pydantic import Field, BaseSettings


class Config(BaseSettings):
    qweather_key: str = ""
    serving_group: list = []
    weather_report_cities = {}
    bad_warning_cities = {}
    apscheduler_config: dict = Field(
        default_factory=lambda: {"apscheduler.timezone": "Asia/Shanghai"})

    class Config:
        extra = "ignore"