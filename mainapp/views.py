from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from lib.wxapi import WxApi
from lib.reply import load_subscribe_reply

# Create your views here.
@csrf_exempt
def keyword(request):
    api_inst = WxApi()
    if request.method == "GET" and \
        "signature" in request.GET:
        signature = request.GET["signature"]
        timestamp = request.GET["timestamp"]
        nonce = request.GET["nonce"]
        echostr = request.GET["echostr"]
        echostr = api_inst.verify(signature, timestamp, nonce, echostr)
        return HttpResponse(echostr)
    elif request.method == "POST":
        body = request.body.decode("utf-8")
        recv_msg = api_inst.receive_msg(body)
        from_user = recv_msg.from_user
        to_user = recv_msg.to_user
        if recv_msg.msg_type == "event" and recv_msg.event == "subscribe":
            content = load_subscribe_reply()
            print(content)
            if not content:
                return HttpResponse("success")

            send_msg = api_inst.create_text_msg(from_user=to_user, to_user=from_user, content=content)
            return HttpResponse(send_msg)


        #send_msg = api_inst.create_text_msg(from_user=recv_msg["to_user"],
        #    to_user=recv_msg["from_user"],
        #    content="how are you")
        #return HttpResponse(send_msg)
