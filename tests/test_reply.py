from django.test import TestCase
import lib.reply

class Test(TestCase):
    def setUp(self):
        pass

    def test_load_subscribe_reply(self):
        lib.reply.load_subscribe_reply()
