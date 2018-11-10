import time
import json
import hashlib
import requests
from lxml import etree
from lib.appsecret import APPID, SECRET
from config import WXAPI_URL

class WxApi(object):
    def __init__(self):
        url = WXAPI_URL + "/token?grant_type=client_credential&appid={}&secret={}".format(APPID, SECRET)
        r = requests.get(url, verify=False)
        content = r.content.decode("utf-8")
        data = json.loads(content)
        self.token = data["access_token"]
        self.expires_in = data["expires_in"]

    def verify(self, signature, timestamp, nonce, echostr):
        token = "shenzhongqiang"
        array = [token, timestamp, nonce]
        array.sort()
        sha1 = hashlib.sha1()
        for x in array:
            sha1.update(x.encode("utf-8"))
        hashcode = sha1.hexdigest()
        if hashcode == signature:
            return echostr
        else:
            return ""

    def get_users(self):
        result = []
        next_openid = None
        while True:
            url = WXAPI_URL + "/user/get?access_token={}".format(self.token)
            print(url)
            if next_openid is not None:
                url = url + "&next_openid={}".format(next_openid)
            r = requests.get(url, verify=False)
            content = r.content.decode("utf-8")
            print(content)
            data = json.loads(content)
            count = data["count"]
            result.extend(data["data"]["openid"])
            next_openid = data["next_openid"]
            if count < 10000:
                break
        return result

    def receive_text_msg(self, msg):
        print(msg)
        root = etree.fromstring(msg)
        to_user = root.xpath('.//ToUserName')[0].text
        from_user = root.xpath('.//FromUserName')[0].text
        msg_type = root.xpath('.//MsgType')[0].text
        msg_id = root.xpath('.//MsgId')[0].text
        content = root.xpath('.//Content')[0].text
        result = {"content": content,
            "from_user": from_user,
            "to_user": to_user
        }
        return result

    def create_text_msg(self, from_user, to_user, content):
        timestamp = int(time.time())
        xml_form = """
        <xml>
        <ToUserName><![CDATA[{to_user}]]></ToUserName>
        <FromUserName><![CDATA[{from_user}]]></FromUserName>
        <CreateTime>{timestamp}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{content}]]></Content>
        </xml>
        """.format(to_user=to_user, from_user=from_user,
            timestamp=timestamp, content=content)
        return xml_form

    def create_menu(self):
        url = WXAPI_URL + "/menu/create?access_token={}".format(self.token)
        body = json.dumps({
            "button":[
                {
                    "type":"click",
                    "name":"今日歌曲",
                    "key":"V1001_TODAY_MUSIC"
                },
                {
                    "name":"菜单",
                    "sub_button":[
                    {
                        "type":"view",
                        "name":"搜索",
                        "url":"http://www.soso.com/"
                    },
                    {
                        "type":"miniprogram",
                        "name":"wxa",
                        "url":"http://mp.weixin.qq.com",
                        "appid":"wx286b93c14bbf93aa",
                        "pagepath":"pages/lunar/index"
                    },
                    {
                        "type":"click",
                        "name":"赞一下我们",
                        "key":"V1001_GOOD"
                    }]
                }
            ]
        })

if __name__ == "__main__":
    inst = WxApi()
