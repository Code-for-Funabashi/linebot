from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
import os, json

import requests

import datetime
# Create your views here.

LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
LINE_ACCESS_TOKEN = os.environ["LINE_ACCESS_TOKEN"]
from django.views.decorators.csrf import csrf_exempt

# for schedule calculation.
today = datetime.datetime.now()
td = today.date()
curr_day = td.day
curr_weekday = today.date().weekday()
weekday_of_first_day = td.replace(day=1).weekday()
curr_month = td.month
weekdays = []
for d in range(1, 8):
    weekdays.append((d, (weekday_of_first_day + d - 1)%7))

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






def get_next_trash_day_of(garbage_type, area_code):
    
    # TODO: dayOfWeekから次の{garbage_type}のゴミの日を計算してくれるmethod
    # areaの指定
    # area = "夏見5～7丁目"
    # >>> get_trash_info_area_of(area)
    # The information is retrieved from the below site.
    # "https://www.city.funabashi.lg.jp/kurashi/gomi/001/p001523.html"
    # 
    trash_info = get_trash_info_area_of(area_code)
    datetime.datetime.now()
    # get 
    trash_info[garbage_type]
    import calendar
    day = 2
    times = 3
    garbage_type = "燃えるゴミ"
    first_target_weekday = list(filter(lambda x: x[1] == day, weekdays))
    if len(first_target_weekday) == 1:
        # get day first_target_weekday[0][0]
        # 対象となる第{times}{day}曜日 (times - 1) * 7
        target_day = first_target_weekday[0][0] + (times - 1) * 7
    return f"{curr_month}月の{target_day}日が{garbage_type}を捨てる日だよ！"



def get_trash_info_area_of(area) -> dict:
    # TODO: get data from area_trash_days table
    # we have to retrieve info like the sample_natsume 
    # "mon":0, "tue":1, "wed":2, "thu":3, "fri":4, "sat":5, "sun":6
    # According to pandas document, the day of the week with Monday=0, Sunday=6.
    sample_natsume = {"burnable":"火金-(夜)",
                    "non_burnable":"3木",  "Resources・PET" : "水", "valuables" : "水"}
    # 
    return sample_natsume




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




def get_message_body(text, text_type):
    # TODO: test quick reply message function.
    return {
        "type": "text",
        "text": "Select your favorite food category or send me your location!",
        "quickReply": {
            "items": [
            {
                "type": "action",
                # "imageUrl": "https://example.com/tempura.png",
                "action": {
                "type": "message",
                "label": "Remind",
                "text": "Remind"
                }
            },
            {
                "type": "action",
                "action": {
                "type": "location",
                "label": "Send location"
                }
            }
            ]
        }
        }