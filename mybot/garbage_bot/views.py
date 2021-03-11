from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
import os, json, re

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
first_weekdays = []
for d in range(1, 8):
    first_weekdays.append((d, (weekday_of_first_day + d - 1)%7))

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
                print(event)
                reply_token = event['replyToken']
                message_type = event['message']['type']

                if message_type == 'text':
                    text = event['message']['text']
                    content_type = parse_message(text)

                    # 応答 bot を呼ぶ
                    choose_response(content_type)
                    # reply += tool.reply_text(reply_token, text)
        return HttpResponse(status=200)



def parse_message(msg):
    # TODO: 燃えるゴミ・燃えないゴミの日を通知する。
    # NLP技術用いていずれ高度化する
    garbage_type = "burnable"
    if "燃える" in msg:
        pass
    elif "燃えない" in msg:
        garbage_type = "non_burnable"
    elif "ゴミ" in msg and re.match("？|?", msg):
        garbage_type = "next_ask_trash_type"
    else:
        garbage_type = "unknown"
    return garbage_type


def choose_response(content_type):
    if content_type == "next_ask_trash_type":
        reply_msg(reply_token, "ありがとうございますー！何のゴミの収集日を聞きたいですか？")
    elif content_type == "unknown":
        reply_msg(reply_token, "ふなっしー？ふなっしーとは付かず離れずの距離を保っていたい")
    else:
        trash_info = get_next_trash_day_of(garbage_type, area_code)
        reply_msg(reply_token, trash_info)




def get_next_trash_day_of(garbage_type, area_code):
    
    # TODO: dayOfWeekから次の{garbage_type}のゴミの日を計算してくれるmethod
    # areaの指定
    # area = "夏見5～7丁目"
    # >>> get_trash_info_area_of(area)
    # The information is retrieved from the below site.
    # "https://www.city.funabashi.lg.jp/kurashi/gomi/001/p001523.html"
    # 
    trash_info = get_trash_info_area_of(area_code)
    # get 
    when2collect = trash_info[garbage_type]
    import calendar
    nthWeek, weekdays, day_or_night= when2collect.split("/")
    weekdays = [int(wd) for wd in weekdays]
    first_target_weekday = list(filter(lambda x: x[1] in weekdays, first_weekdays))
    if len(first_target_weekday) == 1:
        # get day first_target_weekday[0][0]
        # 対象となる第{nthWeek}{day}曜日 (nthWeek - 1) * 7
        target_day = first_target_weekday[0][0] + (int(nthWeek) - 1) * 7
    elif len(first_target_weekday) >= 2: # 可燃ごみ
        return "ちょっと手元の台帳には書いてないわ、ごめんよ"
        pass
    else:
        return "ちょっとわからんかったわ"
    return f"{curr_month}月の{target_day}日が{garbage_type}を捨てる日だよ！"



def get_trash_info_area_of(area) -> dict:
    # TODO: get data from area_trash_days table
    # we have to retrieve info like the sample_natsume 
    # "mon":0, "tue":1, "wed":2, "thu":3, "fri":4, "sat":5, "sun":6
    # According to pandas document, the day of the week with Monday=0, Sunday=6.
    # syntax: {1}/{2}/{3}
    #   {1}: n-th week or every week (-1)
    #   {2}: weekdays
    #   {3}: day or night (or no information if blank)
    sample_natsume = {"burnable":"-1/1,2/night",
                    "non_burnable":"3/3/",  "Resources・PET" : "-1/2/", "valuables" : "-1/2/"}
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