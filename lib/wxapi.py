import os
import time
import json
import hashlib
import yaml
import requests
from lxml import etree
from lib.appsecret import APPID, SECRET
from config import WXAPI_URL

class Msg(object):
    def __init__(self, from_user, to_user, timestamp, msg_type):
        self.from_user = from_user
        self.to_user = to_user
        self.timestamp = timestamp
        self.msg_type = msg_type

class TextMsg(Msg):
    def __init__(self, from_user, to_user, timestamp,
        content, msg_id=None):
        super().__init__(from_user, to_user, timestamp, msg_type="text")
        self.content = content
        self.msg_id = msg_id

    def __repr__(self):
        return '<TextMsg content="{}">'.format(self.content)

class ImageMsg(Msg):
    def __init__(self, from_user, to_user, timestamp,
        pic_url, media_id, msg_id=None):
        super().__init__(from_user, to_user, timestamp, msg_type="image")
        self.pic_url = pic_url
        self.media_id = media_id
        self.msg_id = msg_id

    def __repr__(self):
        return '<ImageMsg pic_url="{}">'.format(self.pic_url)

class VoiceMsg(Msg):
    def __init__(self, from_user, to_user, timestamp,
        media_id, format, msg_id=None):
        super().__init__(from_user, to_user, timestamp, msg_type="voice")
        self.media_id = media_id
        self.format = format
        self.msg_id = msg_id

    def __repr__(self):
        return '<VoiceMsg content="{}">'.format(self.media_id)

class VideoMsg(Msg):
    def __init__(self, from_user, to_user, timestamp,
        media_id, thumb_id, msg_id=None):
        super().__init__(from_user, to_user, timestamp, msg_type="video")
        self.media_id = media_id
        self.thumb_id = thumb_id
        self.msg_id = msg_id

    def __repr__(self):
        return '<VideoMsg content="{}">'.format(self.media_id)

class ShortvideoMsg(Msg):
    def __init__(self, from_user, to_user, timestamp,
        media_id, thumb_id, msg_id=None):
        super().__init__(from_user, to_user, timestamp, msg_type="shortvideo")
        self.media_id = media_id
        self.thumb_id = thumb_id
        self.msg_id = msg_id

    def __repr__(self):
        return '<ShortvideoMsg content="{}">'.format(self.media_id)

class LocationMsg(Msg):
    def __init__(self, from_user, to_user, timestamp,
        location_x, location_y, scale, label, msg_id=None):
        super().__init__(from_user, to_user, timestamp, msg_type="location")
        self.location_x = location_x
        self.location_y = location_y
        self.scale = scale
        self.label = label
        self.msg_id = msg_id

    def __repr__(self):
        return '<LocationMsg location_x="{}" location_y="{}">'.format(self.location_x, self.location_y)

class LinkMsg(Msg):
    def __init__(self, from_user, to_user, timestamp,
        title, desc, url, msg_id=None):
        super().__init__(from_user, to_user, timestamp, msg_type="link")
        self.title = title
        self.desc = desc
        self.url = url
        self.msg_id = msg_id

    def __repr__(self):
        return '<LinkMsg content="{}">'.format(self.desc)

class EventMsg(Msg):
    def __init__(self, from_user, to_user, timestamp,
        event, event_key=None, ticket=None,
            latitude=None, longitude=None, precision=None):
        super().__init__(from_user, to_user, timestamp, msg_type="event")
        self.event = event
        self.event_key = event_key
        self.ticket = ticket
        self.latitude = latitude
        self.longitude = longitude
        self.precision = precision

    def __repr__(self):
        return '<EventMsg content="{}">'.format(self.event)

class WxApi(object):
    def __init__(self):
        url = WXAPI_URL + "/token?grant_type=client_credential&appid={}&secret={}".format(APPID, SECRET)
        r = requests.get(url, verify=False, timeout=5)
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
            if next_openid is not None:
                url = url + "&next_openid={}".format(next_openid)
            r = requests.get(url, verify=False, timeout=5)
            content = r.content.decode("utf-8")
            print(content)
            data = json.loads(content)
            count = data["count"]
            result.extend(data["data"]["openid"])
            next_openid = data["next_openid"]
            if count < 10000:
                break
        return result

    def save_auto_reply(self):
        url = WXAPI_URL + "/get_current_autoreply_info?access_token={}".format(self.token)
        r = requests.get(url, verify=False, timeout=5)
        content = r.content.decode("utf-8")
        data = json.loads(content)
        add_friend_autoreply = data["add_friend_autoreply_info"]
        keyword_list = data["keyword_autoreply_info"]["list"]
        folder = os.path.dirname(__file__)
        filepath = os.path.join(folder, '../', "data/text_reply.yaml")
        result = {}
        for item in keyword_list:
            rule_name = item["rule_name"]
            keywords = list(map(lambda x: x["content"], item["keyword_list_info"]))
            keyword = keywords[0]
            replies = item["reply_list_info"]
            result[keyword] = replies
        with open(filepath, "w") as f:
            yaml.dump(result, f, default_flow_style=False, encoding="utf-8", allow_unicode=True)

    def load_auto_reply(self):
        folder = os.path.dirname(__file__)
        filepath = os.path.join(folder, '../', "data/text_reply.yaml")
        with open(filepath, "r") as f:
            result = yaml.load(f)
            return result

    def receive_msg(self, msg):
        root = etree.fromstring(msg)
        msg_type = root.xpath('.//MsgType')[0].text
        if msg_type == "event":
            return self.receive_event_msg(msg)
        elif msg_type == "text":
            return self.receive_text_msg(msg)
        elif msg_type == "image":
            return self.receive_image_msg(msg)
        elif msg_type == "voice":
            return self.receive_voice_msg(msg)
        elif msg_type == "video":
            return self.receive_video_msg(msg)
        elif msg_type == "shortvideo":
            return self.receive_shortvideo_msg(msg)
        elif msg_type == "location":
            return self.receive_location_msg(msg)
        elif msg_type == "link":
            return self.receive_link_msg(msg)
        elif msg_type == "music":
            return self.receive_music_msg(msg)
        elif msg_type == "news":
            return self.receive_news_msg(msg)

    def receive_text_msg(self, msg):
        print(msg)
        root = etree.fromstring(msg)
        to_user = root.xpath('.//ToUserName')[0].text
        from_user = root.xpath('.//FromUserName')[0].text
        msg_type = root.xpath('.//MsgType')[0].text
        msg_id = root.xpath('.//MsgId')[0].text
        content = root.xpath('.//Content')[0].text
        timestamp = root.xpath('.//CreateTime')[0].text
        msg = TextMsg(from_user, to_user, timestamp,
            content, msg_id)
        return msg

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

    def receive_event_msg(self, msg):
        print(msg)
        root = etree.fromstring(msg)
        to_user = root.xpath('.//ToUserName')[0].text
        from_user = root.xpath('.//FromUserName')[0].text
        msg_type = root.xpath('.//MsgType')[0].text
        event = root.xpath('.//Event')[0].text
        timestamp = root.xpath('.//CreateTime')[0].text
        if event == "subscribe" or event == "unsubscribe":
            msg = EventMsg(from_user, to_user, timestamp, event)
            return msg
        if event == "SCAN":
            pass
        if event == "LOCATION":
            pass
        if event == "CLICK":
            pass

        return result

    def receive_image_msg(self, msg):
        print(msg)
        root = etree.fromstring(msg)
        to_user = root.xpath('.//ToUserName')[0].text
        from_user = root.xpath('.//FromUserName')[0].text
        msg_type = root.xpath('.//MsgType')[0].text
        msg_id = root.xpath('.//MsgId')[0].text
        pic_url = root.xpath('.//PicUrl')[0].text
        media_id = root.xpath('.//MediaId')[0].text
        timestamp = root.xpath('.//CreateTime')[0].text
        msg = ImageMsg(from_user, to_user, timestamp,
            pic_url, media_id, msg_id)
        return msg

    def receive_voice_msg(self, msg):
        print(msg)
        root = etree.fromstring(msg)
        to_user = root.xpath('.//ToUserName')[0].text
        from_user = root.xpath('.//FromUserName')[0].text
        msg_type = root.xpath('.//MsgType')[0].text
        msg_id = root.xpath('.//MsgId')[0].text
        media_id = root.xpath('.//MediaId')[0].text
        timestamp = root.xpath('.//CreateTime')[0].text
        vformat = root.xpath('.//Format')[0].text
        msg = VoiceMsg(from_user, to_user, timestamp,
            media_id, vformat, msg_id)
        return msg

    def receive_video_msg(self, msg):
        print(msg)
        root = etree.fromstring(msg)
        to_user = root.xpath('.//ToUserName')[0].text
        from_user = root.xpath('.//FromUserName')[0].text
        msg_type = root.xpath('.//MsgType')[0].text
        msg_id = root.xpath('.//MsgId')[0].text
        media_id = root.xpath('.//MediaId')[0].text
        timestamp = root.xpath('.//CreateTime')[0].text
        thumb_id = root.xpath('.//ThumbMediaId')[0].text
        msg = VideoMsg(from_user, to_user, timestamp,
            media_id, thumb_id, msg_id)
        return msg

    def receive_shortvideo_msg(self, msg):
        print(msg)
        root = etree.fromstring(msg)
        to_user = root.xpath('.//ToUserName')[0].text
        from_user = root.xpath('.//FromUserName')[0].text
        msg_type = root.xpath('.//MsgType')[0].text
        msg_id = root.xpath('.//MsgId')[0].text
        media_id = root.xpath('.//MediaId')[0].text
        timestamp = root.xpath('.//CreateTime')[0].text
        thumb_id = root.xpath('.//ThumbMediaId')[0].text
        msg = ShortvideoMsg(from_user, to_user, timestamp,
            media_id, thumb_id, msg_id)
        return msg

    def receive_music_msg(self, msg):
        print(msg)
        pass

    def receive_location_msg(self, msg):
        print(msg)
        root = etree.fromstring(msg)
        to_user = root.xpath('.//ToUserName')[0].text
        from_user = root.xpath('.//FromUserName')[0].text
        msg_type = root.xpath('.//MsgType')[0].text
        msg_id = root.xpath('.//MsgId')[0].text
        location_x = root.xpath('.//Location_X')[0].text
        location_y = root.xpath('.//Location_Y')[0].text
        timestamp = root.xpath('.//CreateTime')[0].text
        scale = root.xpath('.//Scale')[0].text
        label = root.xpath('.//Label')[0].text
        msg = LocationMsg(from_user, to_user, timestamp,
            location_x, location_y, scale, label, msg_id)
        return msg

    def receive_link_msg(self, msg):
        print(msg)
        root = etree.fromstring(msg)
        to_user = root.xpath('.//ToUserName')[0].text
        from_user = root.xpath('.//FromUserName')[0].text
        msg_type = root.xpath('.//MsgType')[0].text
        msg_id = root.xpath('.//MsgId')[0].text
        timestamp = root.xpath('.//CreateTime')[0].text
        title = root.xpath('.//Title')[0].text
        desc = root.xpath('.//Description')[0].text
        url = root.xpath('.//Url')[0].text
        msg = ShortvideoMsg(from_user, to_user, timestamp,
            title, desc, url, msg_id)
        return msg

    def receive_news_msg(self, msg):
        print(msg)
        pass

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
