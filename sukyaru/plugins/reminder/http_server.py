import os
from flask import Flask
from flask import request
import httpx
from model import get_qq

app = Flask("remind")
host = "0.0.0.0"
port = 43967

@app.route("/remind", methods=["GET"])
def send_remind_by_get():

    key = request.args.get("key")
    text = request.args.get("text")

    if (key is None) or (text is None):
        return "<p>Cant get key or text:</p><p>key=%s</p><p>text=%s</p>"%(key, text)

    user_qq = get_qq(str(key))

    if user_qq is None:
        return "<p>Cant get user'qq with given key:</p><p>key=%s</p><p>text=%s</p>"%(key, text)

    send_result = httpx.get(
        "http://127.0.0.1:5700/send_private_msg?user_id=%d&message=%s&access_token=mxfsukyaru"%(   # port is set in mirai plugin "Onebot"
            user_qq, text
        ),
        timeout=httpx.Timeout(3, read=2),
        proxies={'http': None, 'https': None}
    ).json()

    return "<p>sending remind:</p><p>key=%s</p><p>text=%s</p>"%(key, text)

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=port
    )
