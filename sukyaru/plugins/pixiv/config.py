from pydantic import Field, BaseSettings


class Config(BaseSettings):
    serving_group = []
    proxy_port = 0
    pixiv_refresh_token = ""
    illu_default_num = 3
    illu_max_num = 5
    illu_tmp_dir = "/tmp/sukyaru/"
    apscheduler_config: dict = Field(
        default_factory=lambda: {"apscheduler.timezone": "Asia/Shanghai"})

    class Config:
        extra = "ignore"