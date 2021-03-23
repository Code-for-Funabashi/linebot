from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
import os, json, re

import requests

import datetime
# Create your views here.

from garbage_bot.models import Remind


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

# 今月分しかデータ取得できないし、何よりglobalで管理するべきではない気がする。
first_weekdays = []
for d in range(1, 8):
    first_weekdays.append((d, (weekday_of_first_day + d - 1)%7))

@csrf_exempt
def callback(request):
    # TODO: This function would be called when linebot was spoken to by user
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
                    choose_response(content_type, text)
                    # reply += tool.reply_text(reply_token, text)
        return HttpResponse(status=200)



def parse_message(msg):
    # TODO: 燃えるゴミ・燃えないゴミの日を通知する。
    # NLP技術用いていずれ高度化する
    garbage_type = "unknown"
    
    if "燃える" in msg:
        garbage_type = "burnable"
    elif "燃えない" in msg:
        garbage_type = "non_burnable"
    elif "ゴミ" in msg and re.findall(r"捨てたい|？", msg):
        garbage_type = "next_ask_trash_type"
    elif len(msg) == 1:
        talk_themes = json.load(open("garbage_bot/statics/talks.json"))
        if talk_themes.get(msg):
            garbage_type = "casual_talk"
    elif "リマインド" in msg:
        garbage_type = "which_trash_type_to_notify"
    else:
        pass
    return garbage_type


def choose_response(content_type, text):
    if content_type == "next_ask_trash_type":
        reply_msg(reply_token, "ありがとうございますー！何のゴミの収集日を聞きたいですか？")
    elif content_type == "unknown":
        reply_msg(reply_token, "ふなっしー？ふなっしーとは付かず離れずの距離を保っていたい")
    elif content_type == "casual_talk":
        talk_themes = json.loads("./statics/talks.json")
        reply_msg(reply_token, talk_themes[text])
    elif garbage_type == "which_trash_type_to_notify":
        # uidごとに過去の会話から、リマインドしたいユーザかを把握、
        # どのゴミの収集日をリマインドするかをユーザに聞く。
        # last_message is which_trash_type_to_notify
        # 3/23: ユーザ対話ログ機能を実装したのち、リマインド機能の実装に入る方がいいかもしれない。
        reply_msg(reply_token, "ありがとうございますー！またリマインドする機能は実装中です。すまんな")
    else:
        # burnable / non_burnable
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
    weekdays = [int(wd) for wd in weekdays.split(",")]
    nthWeek = int(nthWeek)
    first_target_weekday = list(filter(lambda x: x[1] in weekdays, first_weekdays))

    if len(first_target_weekday) == 1:
        # get day first_target_weekday[0][0]
        # 対象となる第{nthWeek}{day}曜日 (nthWeek - 1) * 7
        target_day = first_target_weekday[0][0] + (nthWeek - 1) * 7
    elif len(first_target_weekday) >= 2: 
        # 可燃ごみ
        # import pdb; pdb.set_trace()
        if nthWeek == -1:# every week garbages are collected.
            first_days = [fwd[0] for fwd in first_target_weekday]
            candidate_days = [fd + (nthWeek_ - 1) * 7 for fd in first_days for nthWeek_ in range(1, 6)
                     if fd + (nthWeek_ - 1) * 7 < 32]
            # next dayを見つける
            target_day = min(filter(lambda x: x >= curr_day, candidate_days))
    else:
        return "ちょっとわからんかったわ"
    return f"{curr_month}月の{target_day}日が{garbage_type}を捨てる日だよ！{'時間帯は' + day_or_night + 'だよ' if day_or_night else '' }"



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



def set_reminder():
    """
    朝の時間帯にpush messageを送信するように記録しておく機能
    ---

    CREATE 
    (uuid, when2push, garbage_type) INTO Remind;
    """
    return "TO BE DONE"

def push_remind():
    """
    朝8時に 1-3までを実行する
    1. Execute the following query
        SELECT * WHERE when2push == {str(td)};
    2. QuerySetをuuidごとにまとめ、それぞれのユーザに対してメッセージを送信する。
    """
    today = datetime.date.today()
    # https://bradmontgomery.net/blog/date-lookups-django/
    QuerySet = Remind.objects.filter(
        when2push__day=today.day,
        when2push__year=today.year,
        when2push__month=today.month,
    )
    target_uuids = []
    for q in QuerySet:
        print("Push remind message for ", q.uuid)
        # the pushing processing will be implemented later.
        target_uuids.append(q.uuid)
    return target_uuids



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