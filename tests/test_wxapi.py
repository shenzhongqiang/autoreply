from django.test import TestCase
from lib.wxapi import WxApi

class Test(TestCase):
    def setUp(self):
        self.inst = WxApi()

    def test_get_users(self):
        users = self.inst.get_users()
        print(users)

    def test_save_auto_reply(self):
        self.inst.save_auto_reply()

    def test_load_auto_reply(self):
        self.inst.load_auto_reply()
