from django.test import TestCase, RequestFactory

from .views import *
import datetime
from garbage_bot.models import Remind, GarbageType, Context
from unittest import mock
from django.http import HttpResponse

# Create your tests here.
from django.core.exceptions import ObjectDoesNotExist

from unittest.mock import patch
import json
from django.views.decorators.csrf import csrf_exempt


class Garbage_BotTestCase(TestCase):
    fixtures = [
        "garbage_bot/fixtures/fixture_1.json",
        # "garbage_bot/fixtures/uuid_inclusion.json"
    ]

    def setUp(self):

        Remind.objects.create(
            uuid="test_case:remind",
            # Currently when2push = models.DateField(auto_now=True)
            # We have to consider which datatype we should use; date or datetime.
            when2push=datetime.datetime.now() + datetime.timedelta(minutes=1),
            # ValueError: Cannot assign "1": "Remind.garbage_type" must be a "GarbageType" instance.
            garbage_type=GarbageType.objects.get(garbage_type=1),
        ).save()
        self.parameters_ask_what = [
            ("ほげ", "ちょっと分からん買ったわ。もう一度答えてくれ.可燃ゴミ / 不燃ゴミ / 資源ゴミ / 有価物の中から選んでね！"),
            # TODO:
            # We could not pass the test because we could not take garbage_type in Japanese.
            # ("可燃ごみ", "4月の19日がburnableを捨てる日だよ！時間帯は昼だよ"),
            ("burnable", "5月の31日がburnableを捨てる日だよ！時間帯は昼だよ"),
        ]
        self.parameters_ask_where = [
            # user_id, msg, expected, expected_state
            (
                "test_case:ask_where_state21",
                "旭町",
                {"town_name": "旭町"},
                "OK、さらに何丁目を指定してください！",
                22,
            ),
            (
                "test_case:ask_where_state22_1",
                "1丁目",
                {"district_name": "1丁目"},
                "OK、じゃあ次は捨てたいゴミの種類を教えてね！\n                可燃ゴミ / 不燃ゴミ / 資源ゴミ / 有価物",
                24,
            ),
            (
                "test_case:ask_where_state22_2",
                "2丁目",
                {"district_name": "2丁目"},
                "OK、さらに番地を指定してください！",
                23,
            ),
            # ...
            # ...
        ]

    def test_ask_where(self):
        user_id = "test_case:ask_where"

        for user_id, msg, kv, expected, expected_state in self.parameters_ask_where:
            with self.subTest(p=(user_id, msg)):
                cm = ContextHandler(user_id, msg, reply_token="reply_token")
                self.assertEqual(expected, cm.ask_where(kv))
                self.assertEqual(expected_state, cm.context.state)
        pass

    def test_ask_what(self):
        user_id = "test_case:ask_what"

        def _ask_what(user_id, msg):
            cm = ContextHandler(user_id, msg, reply_token="reply_token")
            actual = cm.ask_what()
            return actual

        # TODO: expected作成
        # 4.17 モデルの更新をfixtureに反映させる。
        # expected = "ちょっと分からん買ったわ。もう一度答えてくれ.可燃ゴミ / 不燃ゴミ / 資源ゴミ / 有価物の中から選んでね！"
        # expected = f"{curr_month}月の{target_day}日が{garbage_type}を捨てる日だよ！{'時間帯は' + day_or_night + 'だよ' if day_or_night else '' }"

        for p, expected in self.parameters_ask_what:
            with self.subTest(p=p):
                self.assertEqual(expected, _ask_what(user_id, p))

    def test_manage_context(self):
        user_id = "test_case:manage_context"
        pass

    def test_get_day_to_collect(self):
        # import pdb;pdb.set_trace()
        # TODO: utc問題解消しておく
        expected = "5月の31日がburnableを捨てる日だよ！時間帯は昼だよ"
        user_id = "test_case:get_day_to_collect"
        try:
            context: Context = Context.objects.filter(uuid=user_id).latest()
            actual = get_day_to_collect(context)
        except ObjectDoesNotExist:
            actual = None

        self.assertEqual(expected, actual)


class ContextHandlerTestCase(TestCase):
    fixtures = [
        "garbage_bot/fixtures/fixture_1.json",
    ]

    def test_get_or_create(self):
        user_id = "new_user"
        cm = ContextHandler(user_id, msg="ゴミ捨てたい", reply_token="testContextHandler")

        qs = Context.objects.filter(uuid=user_id)
        self.assertEqual(len(qs), 1)

    def test_state26(self):
        expected = "Okay I'll set the reminder"
        user_id = "test_case:state26"

        ch = ContextHandler(user_id, msg="うん", reply_token="testSetRemider")
        ch.create_message()
        actual = ch.msg
        self.assertEqual(expected, actual)
        qs = Remind.objects.filter(
            uuid=user_id,
            garbage_type=2,
        )
        self.assertEqual(len(qs), 1)


class CallBackTestCase(TestCase):
    fixtures = [
        "garbage_bot/fixtures/fixture_1.json",
    ]
    test_json = {
        "events": [
            {
                "timestamp": 1475246936807,
                "replyToken": "7304712ea2134a32873646ea2e74c264",
                "message": {"type": "text", "id": "4989775490995", "text": "テスト"},
                "type": "message",
                "source": {"userId": "test_case:get_day_to_collect", "type": "user"},
            }
        ]
    }

    def test_callback(self):

        rf = RequestFactory()
        request = rf.post(
            "/garbage_bot/callback/",
            data=self.test_json,
            content_type="application/json",
        )
        res = callback(request)

        self.assertEqual(res.status_code, 200)


@csrf_exempt
def test_server(request):
    return HttpResponse(status=200)
