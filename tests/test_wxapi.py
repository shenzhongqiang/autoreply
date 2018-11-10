from django.test import TestCase
from lib.wxapi import WxApi

class Test(TestCase):
    def setUp(self):
        self.inst = WxApi()

    def test_get_users(self):
        users = self.inst.get_users()
        print(users)
