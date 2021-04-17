from django.test import TestCase
from .views import *
import datetime
from garbage_bot.models import Remind, GarbageType, Context
from unittest import mock
from django.http import HttpResponse
# Create your tests here.
from django.core.exceptions import ObjectDoesNotExist

class Garbage_BotTestCase(TestCase):
    fixtures = ["garbage_bot/fixtures/fixture_1.json", 
    # "garbage_bot/fixtures/uuid_inclusion.json"
    ]
    def setUp(self):
        # garbage_type, area_code, expected
        self.parameters_type_area = [
        # 日時は各地域ごとに調整していくつか試す。
        # 3/19の段階では、次の燃えるゴミの日は3/23なのでこちらを指定
            ("burnable", "natsume", f"3月の30日がburnableを捨てる日だよ！時間帯はnightだよ"),
            ("non_burnable", "natsume", f"3月の18日がnon_burnableを捨てる日だよ！"), 
        ]
        self.parameters_parse_message = [
            ("燃える", "burnable"),
            ("燃えない", "non_burnable"),
            ("ゴミ捨てたい", "next_ask_trash_type"),
            # ("可燃ゴミ捨てたい？", "burnable"),
            ("あ", "casual_talk"),
            ("ち", "casual_talk"),
            ("？", "unknown"),
        ]
        Remind.objects.create(
            uuid=os.environ["LINE_TEST_UID"],
            # Currently when2push = models.DateField(auto_now=True)
            # We have to consider which datatype we should use; date or datetime.
            when2push=datetime.datetime.now() + datetime.timedelta(minutes=1),
            # ValueError: Cannot assign "1": "Remind.garbage_type" must be a "GarbageType" instance.
            garbage_type=GarbageType.objects.get(garbage_type=1)
        ).save()
        self.parameters_choose_response = [
            (("next_ask_trash_type", "hoge"), "ありがとうございますー！何のゴミの収集日を聞きたいですか？"),
            (("unknown", "hoge"), "ふなっしー？ふなっしーとは付かず離れずの距離を保っていたい"),
            (("casual_talk", "あ"), "アンデルセン公園、騙されたと思って行ってみて"),
            (("casual_talk", "い"), "意外に人気あるんだよ"),
            (("which_trash_type_to_notify", "hoge"), "ありがとうございますー！リマインドする機能は実装中です。すまんな"),
            
        ]
        self.parameters_casual_talks = [
            ("あ", "アンデルセン公園、騙されたと思って行ってみて"),
            ("い", "意外に人気あるんだよ"),
            ("ん", "自分何いうてんねん")
        ]
    wd2id = {"月": 0 , "火": 1, "水": 2, "木":3, "金":4, "土":5, "日": 6}

    def test_ask_what(self):
        user_id = "test_case:ask_what"
        context: Context = Context.objects.filter(uuid=user_id).latest()
        actual = ask_what(context)
        # TODO: expected作成
        # 4.17 モデルの更新をfixtureに反映させる。
        expected = "ちょっと分からん買ったわ。もう一度答えてくれ.\n\
            可燃ゴミ / 不燃ゴミ / 資源ゴミ / 有価物の中から選んでね！"
        # expected = f"{curr_month}月の{target_day}日が{garbage_type}を捨てる日だよ！{'時間帯は' + day_or_night + 'だよ' if day_or_night else '' }"
        self.assertEqual(
            expected, 
            actual    
            )

    def test_manage_context(self):
        user_id = "test_case:manage_context"
        # manage_context(user_id)
        pass

    def test_get_day_to_collect(self):
        # import pdb;pdb.set_trace()
        # TODO: utc問題解消しておく
        expected = "4月の12日がburnableを捨てる日だよ！時間帯は昼だよ"
        user_id = os.environ["LINE_TEST_UID"]
        try:
            context: Context = Context.objects.filter(uuid=user_id).latest()
            actual = get_day_to_collect(context)
        except ObjectDoesNotExist:
            actual = None
        
        self.assertEqual(
            expected, 
            actual    
            )


    # End

    # def test_get_next_trash_day_of(self):
    #     # garbage_type, area_code
    #     for garbage_type, area_code, expected in self.parameters_type_area:
    #         with self.subTest():
    #             self.assertEqual(
    #                 expected, 
    #                 get_next_trash_day_of(garbage_type, area_code)
    #                 )

    def test_get_one_message(self):
        for p, expected in self.parameters_casual_talks:
            with self.subTest(p=p):
                self.assertEqual(expected, get_one_message(p))


    # def test_push_remind(self):
    #     target_uuids = push_remind()
    #     self.assertEqual(target_uuids, [os.environ["LINE_TEST_UID"]])
    #     # when2push

    # def test_parse_message(self):
    #     for p, expected in self.parameters_parse_message:
    #         with self.subTest(p=p):
    #             self.assertEqual(expected, parse_message(p))
    


    # def test_choose_response(self):
    #     for (content_type, text), expected \
    #         in self.parameters_choose_response:
    #         with self.subTest(content_type=content_type, text=text):
    #             self.assertEqual(
    #                 expected, 
    #                 choose_response(content_type, text)
    #                 )
    # def test_get_trash_info_area_of(self):
    #     # return values type check
    #     actual = type(get_trash_info_area_of(area="natsume"))
    #     self.assertEqual(dict, actual)
