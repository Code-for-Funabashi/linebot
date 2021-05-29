import datetime
from django.db import models
import requests
import os
import json
from garbage_bot.models import Area, GarbageType, CollectDay

physical2logical_dict = {
    "burnable": "可燃ゴミ",
    "non_burnable": "不燃ゴミ",
    "resources": "資源ゴミ",
    "valuables": "有価物",
    "town_name": "町名",
    "district_name": "何丁目",
    "address_name": "番地",
}

logical2physical_dict = {v: k for k, v in physical2logical_dict.items()}


def push_msg(user, text):
    url = os.environ["LINE_PUSH_ENDPOINT"]
    user_list = [user]
    body = {"to": user_list, "messages": [{"type": "text", "text": text}]}
    res = requests.post(
        url,
        headers={
            "Content-Type": "application/json",
            "Authorization": f'Bearer {os.environ["ACCESS_TOKEN_"]}',
        },
        data=json.dumps(body),
    )
    assert res.status_code == 200


def reply_msg(reply_token, text):

    url = os.environ["LINE_ENDPOINT"]
    body = {
        "replyToken": reply_token,
        "messages": [
            {"type": "text", "text": text},
        ],
    }
    res = requests.post(
        url,
        headers={
            "Content-Type": "application/json",
            "Authorization": f'Bearer {os.environ["ACCESS_TOKEN_"]}',
        },
        data=json.dumps(body),
    )
    assert res.status_code == 200
    return "DONE"


def quick_reply(reply_token, text, choices):

    url = os.environ["LINE_ENDPOINT"]

    choice_list = [
        {
            "type": "action",
            "action": {"type": "message", "text": c_text, "label": c_text},
        }
        for c_text in choices
    ]
    body = {
        "replyToken": reply_token,
        "type": "text",
        "text": text,
        "messages": [
            {
                "type": "text",
                "text": text,
                "quickReply": {
                    "items": choice_list
                    # + [
                    # {
                    #     "type": "action",
                    #     "action": {
                    #     "type": "location",
                    #     "label": "Send location"
                    #     }
                    # }]
                },
            },
        ],
    }
    res = requests.post(
        url,
        headers={
            "Content-Type": "application/json",
            "Authorization": f'Bearer {os.environ["ACCESS_TOKEN_"]}',
        },
        data=json.dumps(body),
    )
    assert res.status_code == 200
    return "DONE"


def get_json(row, idx):
    out_list = []

    BURNABLE_WD = 2
    DAY_NIGHT_COLUMN = 3
    NON_BURNABLE_WD = 4
    RESOURCE = 5
    VALUABLES = 6
    DISTRICT_COL = 7
    for garbage_type in range(1, 5):

        # town_name = row["town_name"]
        # district_name = row["district_name"]

        nth_week = -1  # 不燃ごみのみ利用する。他のごみは毎週収集する
        day_or_night = -1  # 昼夜の指定がされているのは可燃ごみだけ

        # sample_df indexをarea_idにしているので　name propertyで取得
        area_id = idx + 1

        district_info = row[DISTRICT_COL]
        if garbage_type == 1:
            day_or_night = row[DAY_NIGHT_COLUMN]
            weekday_info = row[BURNABLE_WD]

        elif garbage_type == 2:  # non_burnable
            nth_week = row[8]
            weekday_info = row[9]

        elif garbage_type == 3:  # resources / 資源
            weekday_info = row[RESOURCE]

        elif garbage_type == 4:  # 有価物
            weekday_info = row[VALUABLES]

        out_list.append(
            {
                "area_id": Area(area_id),
                # "town_name": town_name,
                # "district_name": district_name,
                "garbage_type": GarbageType(garbage_type),
                "day_or_night": day_or_night,
                "nth_week": nth_week,
                "weekday_info": weekday_info,
                # "district_info": "none" if district_info else district_info
            }
        )
    return out_list


# def get_context_or_none(Model: models.Model, user_id):

#     try:
#         context: Context = Context.objects.filter(uuid=user_id).latest()
#         actual = get_day_to_collect(context)
#     except ObjectDoesNotExist:
#         actual = None


def get_logical_name(physical_name):
    return physical2logical_dict[physical_name]


# TODO:
# 曜日情報をどうとるべきか再検討する。
# for schedule calculation.
# FIXME:
# この仕様だと、curr_monthが12月の時に nextmonth:1月になるので、
# curr_yearの修正をしないといけないが出来ていない。
td = datetime.datetime.now()

curr_weekday = td.date().weekday()
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
        first_weekdays.append((d, (wd_1st + d - 1) % 7))
    return first_weekdays
