from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
import os, json

import requests

import datetime
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
                    reply_msg(reply_token, "ふなっしー？ふなっしーとは付かず離れずの距離を保っていたい")
                    # reply += tool.reply_text(reply_token, text)
        return HttpResponse(status=200)



def parse_message(msg):
    # TODO: 燃えるゴミ・燃えないゴミの日を通知する。
    # NLP技術用いていずれ高度化する
    garbage_type = "flammable"
    if "燃える" in msg:
        pass
    elif "燃えない" in msg:
        garbage_type = "inflammable"
    else:
        garbage_type = "unknown"
    return garbage_type




def get_next_trash_day_of(garbage_type):

    # TODO: dayOfWeekから次の{garbage_type}のゴミの日を計算してくれるmethod
    pass




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

