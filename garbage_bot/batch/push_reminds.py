""" 
Batch functions can be executed using Custom command
(https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/)
"""
from garbage_bot.models import (
    Remind,
    Area,
    CollectDay,
    Context,
    GarbageType,
)
import datetime
import requests


def push_remind():
    """
    朝8時に 1-3までを実行する
    1. Execute the following query
        SELECT * WHERE when2push == {str(td)};
    2. QuerySetをuuidごとにまとめ、それぞれのユーザに対してメッセージを送信する。
    """
    today = datetime.date.today()
    # https://bradmontgomery.net/blog/date-lookups-django/
    for gtype in range(1, 5):
        # 4 types of garbage
        QuerySet = Remind.objects.filter(
            when2push__day=today.day,
            when2push__year=today.year,
            when2push__month=today.month,
            garbage_type=gtype,
        )

        target_users = []
        for q in QuerySet:
            print("Push remind message for ", q.uuid)
            # the pushing processing will be implemented later.
            target_users.append(q.uuid)

        url = os.environ["LINE_PUSH_ENDPOINT"]
        body = {
            "to": target_users,
            "messages": [
                {
                    "type": "text",
                    "text": f"This is a remind test:\
                        For {gtype} at {today.year}/{today.month}/{today.day}",
                }
            ],
        }

        res = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {ACCESS_TOKEN}",
            },
            data=json.dumps(body),
        )
