from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
import os, json

import requests
# Create your views here.

LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
LINE_ACCESS_TOKEN = os.environ["LINE_ACCESS_TOKEN"]
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def callback(request):
    # TODO: This function would be called when linebot was spoken by user
    # 
    # 
    # import pdb; pdb.set_trace()
    if request.method == 'POST':
        request_json = json.loads(request.body.decode('utf-8'))
        # リクエストが空でないことを確認
        if(request_json != None):

            # イベントの取得
            # import pdb;pdb.set_trace()
            for event in request_json['events']:
                reply_token = event['replyToken']
                message_type = event['message']['type']

                if message_type == 'text':
                    text = event['message']['text']

                    # 応答 bot を呼ぶ
                    reply_msg(reply_token, "ふなっしーとは付かず離れずの距離を保っていたい")
                    # reply += tool.reply_text(reply_token, text)
        return HttpResponse(status=200)





def reply_msg(reply_token, text):
    url = "https://api.line.me/v2/bot/message/reply"
    body = {
        "replyToken":reply_token,
        "messages":[
            {
                "type":"text",
                "text":f"Hello, user\n {text}"
            },
            ]
    }

        
    requests.post(url, 
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'},
        data=json.dumps(body)
    )
    return "DONE"

