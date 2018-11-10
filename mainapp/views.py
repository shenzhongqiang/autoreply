from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from lib.wxapi import WxApi

# Create your views here.
@csrf_exempt
def keyword(request):
    if request.method == "GET" and \
        "signature" in request.GET:
        signature = request.GET["signature"]
        timestamp = request.GET["timestamp"]
        nonce = request.GET["nonce"]
        echostr = request.GET["echostr"]
        api_inst = WxApi()
        echostr = api_inst.verify(signature, timestamp, nonce, echostr)
        return HttpResponse(echostr)
    elif request.method == "POST":
        body = request.body.decode("utf-8")
        api_inst = WxApi()
        recv_msg = api_inst.receive_text_msg(body)
        send_msg = api_inst.create_text_msg(from_user=recv_msg["to_user"],
            to_user=recv_msg["from_user"],
            content="how are you")
        return HttpResponse(send_msg)
