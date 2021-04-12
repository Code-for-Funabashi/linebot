from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
import os, json, re

import requests

import datetime
# Create your views here.

from garbage_bot.models import Remind, Area, CollectDay, Context


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

                # 1. Extract UID
                # 2. Get the latest context
                # manage_context

                if message_type == 'text':
                    text = event['message']['text']

                    # 3. parse_message
                    content_type = parse_message(text)


                    # context

                    # 応答 bot を呼ぶ
                    reply = choose_response(content_type, text)
                    # make a request.
                    reply_msg(reply_token, reply)
                    # reply += tool.reply_text(reply_token, text)
    return HttpResponse(reply, status=200)



# 過去のお話を踏まえて、話す内容決める
def manage_context(user_id):

    # return 
    #   next_method: 次に利用する関数を返す？
    QuerySet = Context.objects.get_or_none(uuid=user_id)
    status = QuerySet.latest().status
    if status == 0:
        pass
    # 1文字遊びしてきた
    elif status == 1:
        pass
    # ゴミ収集日を聞いてきた
    elif status == 2:
        # check whether context has "where" and "what"
        # 
        # CODE HERE!
        # ask_what()
        # ask_where()
        pass
    # ゴミリマインドをお願いしてきた
    elif status == 3:
        # check whether context has "where" and "what"
        # 
        # CODE HERE!
        # ask_what()
        # ask_where()
        pass
    # やりとり終わったで or やりとりの途中で一日経っちゃったよ笑
    elif status == 4:
        pass

# status == None(新規ユーザ)の場合、新しいセッションを発行する
# status == 4の場合、新しいセッションを発行する
# 今発話された内容を精査する
def parse_message(msg):
    # TODO: 燃えるゴミ・燃えないゴミの日を通知する。
    # 
    # return: 
    #   content_type: 次の状態を返す
    content_type = 0
    
    if "ゴミ" in msg and re.findall(r"捨てたい|？", msg):
        content_type = 2
    elif len(msg) == 1:
        talk_themes = json.load(open("garbage_bot/statics/talks.json"))
        if talk_themes.get(msg):
            content_type = 1
    elif "リマインド" in msg:
        content_type = 3
    else:
        pass
    return content_type

# status == 1の場合、
def get_one_message(msg):
    talk_themes = json.load(open("garbage_bot/statics/talks.json"))
    if talk_themes.get(msg):
        return talk_themes[msg]
    else:
        return "自分何いうてんねん"

# status == 2の場合、ask_what()/ask_where()/get_day_to_collect()
# status == 3の場合、ask_what()/ask_where()/get_day_to_collect()
def ask_what(context):
    # quick replies
    pass

def ask_where():
    # quick replies
    pass
def get_day_to_collect(context):

    garbage_type = context.garbage_type
    area_id = context.area_id
    ret_message = get_next_trash_day_of(garbage_type, area_id)
    return ret_message

def get_next_trash_day_of(garbage_type, area_code):
    
    # TODO: dayOfWeekから次の{garbage_type}のゴミの日を計算してくれるmethod
    # areaの指定
    # area = "夏見5～7丁目"
    # >>> get_trash_info_area_of(area)
    # The information is retrieved from the below site.
    # "https://www.city.funabashi.lg.jp/kurashi/gomi/001/p001523.html"
    # 
    nthWeek, weekdays, day_or_night = get_trash_info_area_of(garbage_type, area_code)
    
    print(nthWeek, weekdays, day_or_night)
    
    day_or_night = "昼" if day_or_night == 1 else "夜"
    import calendar
    weekdays = [int(wd) for wd in weekdays.split(",")]
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


def choose_response(content_type, text):
    if content_type == "next_ask_trash_type":
        reply = "ありがとうございますー！何のゴミの収集日を聞きたいですか？"
    elif content_type == "unknown":
        reply = "ふなっしー？ふなっしーとは付かず離れずの距離を保っていたい"
    elif content_type == "casual_talk":
        talk_themes = json.load(open("garbage_bot/statics/talks.json"))
        reply = talk_themes[text]
    elif content_type == "which_trash_type_to_notify":
        # uidごとに過去の会話から、リマインドしたいユーザかを把握、
        # どのゴミの収集日をリマインドするかをユーザに聞く。
        # last_message is which_trash_type_to_notify
        # 3/23: ユーザ対話ログ機能を実装したのち、リマインド機能の実装に入る方がいいかもしれない。
        reply = "ありがとうございますー！リマインドする機能は実装中です。すまんな"
    else:
        # burnable / non_burnable
        trash_info = get_next_trash_day_of(garbage_type, area_code)
        reply = trash_info
    return reply



def get_trash_info_area_of(garbage_type, area_id) -> tuple:
    # TODO: get data from area_trash_days table
    # we have to retrieve info like the sample_natsume 
    # "mon":0, "tue":1, "wed":2, "thu":3, "fri":4, "sat":5, "sun":6
    # According to pandas document, the day of the week with Monday=0, Sunday=6.
    # syntax: {1}/{2}/{3}
    #   {1}: n-th week or every week (-1)
    #   {2}: weekdays
    #   {3}: day or night (or no information if blank)
    
    # garbage_type, area_idから収集日情報を取得
    collect_day:CollectDay = CollectDay.objects.get(garbage_type=garbage_type, area_id=area_id)
    nthWeek: int = collect_day.nth_week
    weekdays: str = collect_day.weekday_info
    day_or_night: int = collect_day.day_or_night

    return nthWeek, weekdays, day_or_night



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
    url = os.environ["LINE_ENDPOINT"]
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