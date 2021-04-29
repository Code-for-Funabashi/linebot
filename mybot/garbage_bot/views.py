from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
import os, json, re

import requests

import datetime
# Create your views here.

from garbage_bot.models import (
    Remind, Area, CollectDay,
    Context, GarbageType,
    )
from django.views.decorators.csrf import csrf_exempt

CHANNEL_SECRET = os.environ["CHANNEL_SECRET_"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN_"]

# TODO:
# 曜日情報をどうとるべきか再検討する。
# for schedule calculation.
td = datetime.datetime.now()
curr_day = td.day
curr_weekday = td.date().weekday()
# weekday_of_first_day = td.replace(day=1).weekday()
curr_month = td.month
curr_year = td.year


def get_first_weekdays(year, month):
    """
        input : year=2021, month=4
        output: [(1, 3), (2, 4), (3, 5), (4, 6), (5, 0), (6, 1), (7, 2)]
              :  means [(2021/04/01, 3(Thu)), (2021/04/02, 4(Fri)), .., (2021/04/07, 2(Wed)]
    """
    from calendar import Calendar
    cal = Calendar()
    first_week = cal.monthdayscalendar(year, month)[0]
    wd_1st = first_week.index(1)
    
    first_weekdays = []
    for d in range(1, 8):
        first_weekdays.append((d, (wd_1st + d - 1)%7))
    return first_weekdays    

@csrf_exempt
def callback(request):
    # TODO: This function would be called when linebot was spoken to by user
    # 
    if request.method == 'POST':
        request_json = json.loads(request.body.decode('utf-8'))
        # リクエストが空でないことを確認
        if(request_json != None):
            # イベントの取得
            for event in request_json['events']:
                print(event)
                reply_token = event['replyToken']
                message_type = event['message']['type']
                user_id = event["source"]["userId"]
                
                if message_type == 'text':
                    # 2. Extract message
                    msg = event['message']['text']
                    # 2. Instanciate a Context Manager.
                    cm = ContextManager(user_id, msg)
                    
                    # make a request.
                    reply_msg(reply_token, cm.receive_msg())
                    # reply += tool.reply_text(reply_token, text)
    return HttpResponse(status=200)



# 過去のお話を踏まえて、話す内容決める
class ContextManager():

    def __init__(self, user_id, msg):
        context: Context = self.get_or_create(user_id)
        self.context = context
        self.msg = msg
        self.reply = None

    def receive_msg(self):
        state = self.context.state
        if state == 0:
            # 何がしたくて話しかけられたかを最初話す
            msg = self.parse_message()

        # # 1文字遊びしてきた
        # elif state // 10 == 1:
        #     get_one_message(self.msg)
        # ゴミ収集日を聞いてきた

        # CODE HERE!
        # どこの地域なのか？
        # elif state == 20:
        #     reply_msg("どこの地域が良いですか？")
        elif state == 21:
        # 21: ask_where聞き終わり
            msg = self.ask_where({"town_name":self.msg})
            
        # with 21 + msg:町名を答えてもらった -> 22
        elif state == 22:
            msg = self.ask_where({"district_name":self.msg})

        # 22: n丁目なのか答えてもらう
        # with 22 + msg:n丁目を答えてもらった -> 23: DONE
        
        elif state == 23:
            msg = self.ask_where({"address_name":self.msg})

        # ask_what()
        # 何捨てたいのか聞く
        elif state == 24:
            msg = self.ask_what()
        # with 24 + msg:garbage_typeを答えてもらった -> 25
        elif state == 25:
            # TODO:
            # ex:「前、教えた情報、前日にリマインドする？」と聞く
            # msgはなんでもいい。
            msg = "前、教えた情報、前日にリマインドする？"
            # if so, execute set_reminder()
        # remider setting
        elif state >= 30:
            # TODO:
            # Already know where to collect/ what type of garbage??
            # 1. check the detail of remind.
            # 2. if not known, retry to ask as we did in state >=20
            msg = "リマインドは実装中なんだわ"
        return msg

    def parse_message(self):
        
        if "ゴミ" in self.msg and re.findall(r"捨てたい|？", self.msg):
            state = 21
            reply_msg_ = "ゴミ捨てたいんですね！"+"どこの地域が良いですか？"
        elif "リマインド" in self.msg:
            state = 31
            reply_msg_ = "リマインド承知！"+"どこの地域が良いですか？"
        else:
            state = 0
            reply_msg_ = "ごめんなさい。も一度何したいか教えてちょ！"

        self.state = state
        return reply_msg_

    def ask_where(self, key_value:dict):
        # inspect the input.

        # FIXME:
        # `area_candidates` is not so good name.
        # it contains the information to specify the location to throw away.
        # the elements are ["town_name", "district_name", "address_name"].
        current_keys = self.context.area_candidates.copy()
        current_keys.update(key_value)
        qs = Area.objects.filter(**current_keys)

        if len(qs) == 0:
            return "んー見つからなかった。もう一度お願い"
        else:
            self.context.area_candidates.update(key_value)
        next_name = None
        for idx, name in enumerate(["town_name", "district_name", "address_name"]):
            if self.context.area_candidates.get(name):
                # last_specified_name = self.context.area_candidates[name]
                continue
            else:
                next_name = name
                break
        if len(qs) == 1:
            # finished to specify where you want to know the day to collect.
            self.update("state", 24) # =>次は聞きたい地域
            # printじゃなくreply msg func使う
            print("OK、じゃあ次は捨てたいゴミの種類を教えてね！\n\
                可燃ゴミ / 不燃ゴミ / 資源ゴミ / 有価物")
        elif len(qs)>1:
            print(f"OK、さらに{next_name}を指定してください！")
            self.update("state", self.context.state + 1)
            # quick reply
        else:
            pass
    def ask_what(self):
        # retreive
        qs = GarbageType.objects.filter(garbage_name=self.msg)
        if len(qs) != 1:
            reply = "ちょっと分からん買ったわ。もう一度答えてくれ.可燃ゴミ / 不燃ゴミ / 資源ゴミ / 有価物の中から選んでね！"
            print(reply)
        # if specified.
        else:
            print("ok! 計算するね。")
            self.update("state", self.context.state + 1)
            self.update("garbage_type", qs[0])
            reply = get_day_to_collect(self.context)
        return reply

    def update(self, key, value):
        setattr(self.context, key, value)
        self.context.save()
    
    def get_or_create(self, user_id):
        
        qs = Context.objects.filter(uuid=user_id)
        if len(qs) == 0:
            context = Context.objects.create(uuid=user_id, state=0)
        else:
            context = qs.latest()
        return context



# -------------------------------------------------------------------------------------
# state == None(新規ユーザ)の場合、新しいセッションを発行する
# state == 4の場合、新しいセッションを発行する
# 今発話された内容を精査する

# state == 1の場合、
def get_one_message(msg):
    talk_themes = json.load(open("garbage_bot/statics/talks.json"))
    if talk_themes.get(msg):
        return talk_themes[msg]
    else:
        return "自分何いうてんねん"

def get_day_to_collect(context: Context):
    
    # trash_collection_days.xlsxの各行の情報がとって来れればいい状態:
    garbage_type = context.garbage_type
    assert garbage_type
    area_candidates = context.area_candidates
    # specify area_id
    qs = Area.objects.filter(**area_candidates)
    assert len(qs) == 1
    area_id = qs[0].pk
    ret_message = get_next_trash_day_of(garbage_type, area_id)
    return ret_message

def get_next_trash_day_of(garbage_type, area_code):
    
    # TODO: dayOfWeekから次の{garbage_type}のゴミの日を計算してくれるmethod
    # areaの指定
    # area = "夏見5～7丁目"
    # >>> get_trash_info_area_of(area)
    # The information is retrieved from the below site.
    # "https://www.city.funabashi.lg.jp/kurashi/gomi/001/p001523.html"
    nthWeek, weekdays, day_or_night = get_trash_info_area_of(garbage_type, area_code)
    
    print(nthWeek, weekdays, day_or_night)

    day_or_night = "昼" if day_or_night == 1 else "夜"
    import calendar
    weekdays = [int(wd) for wd in weekdays.split(",")]
    
    target_month = curr_month

    def get_candidate_days(curr_year, curr_month):
        first_weekdays_current_month = get_first_weekdays(curr_year, curr_month)
        first_target_weekday = list(filter(lambda x: x[1] in weekdays, first_weekdays_current_month))

        if len(first_target_weekday) == 1:
            # get day first_target_weekday[0][0]
            # 対象となる第{nthWeek}{day}曜日 (nthWeek - 1) * 7
            if nthWeek > 0:
                candidate_days = first_target_weekday[0][0] + (nthWeek - 1) * 7
            else:
                # 毎週収集される場合
                first_days = [fwd[0] for fwd in first_target_weekday]
                candidate_days = [fd + (nthWeek_ - 1) * 7 for fd in first_days for nthWeek_ in range(1, 6)
                        if fd + (nthWeek_ - 1) * 7 < 32]

        elif len(first_target_weekday) >= 2: 
            # 可燃ごみ
            if nthWeek == -1:# every week garbages are collected.
                first_days = [fwd[0] for fwd in first_target_weekday]
                candidate_days = [fd + (nthWeek_ - 1) * 7 for fd in first_days for nthWeek_ in range(1, 6) if fd + (nthWeek_ - 1) * 7 < 32]
        else:
            # maybe not occurred.
            raise Exception("IRREGULAR PATTERN")
        return candidate_days
    
    
    def calculate_closest_day_in_same_month(candidate_days, target_month):
        get_date_obj = lambda x: datetime.datetime(year=curr_year, month=target_month, day=x, hour=1)
        filter_ = [x for x in candidate_days if get_date_obj(x) >= td]
        if sum(filter_):#existing case
            return min(filter_)
        else:# does not case
            return None

    # 今月の対象日が既に過ぎている場合があるため、今月・来月分けて候補日を計算する必要がある
    candidate_days = get_candidate_days(curr_year, curr_month)
    target_day = calculate_closest_day_in_same_month(candidate_days, target_month)
    if target_day is None:
        # Then re-calculate the target day at next month.
        target_month = curr_month + 1
        candidate_days = get_candidate_days(curr_year, target_month)
        target_day = calculate_closest_day_in_same_month(candidate_days, target_month)
        

    return f"{target_month}月の{target_day}日が{garbage_type}を捨てる日だよ！{'時間帯は' + day_or_night + 'だよ' if day_or_night else '' }"




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
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {ACCESS_TOKEN}'},
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