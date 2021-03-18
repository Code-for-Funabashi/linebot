from django.test import TestCase
from .views import *
# Create your tests here.

class Garbage_BotTestCase(TestCase):
    def setUp(self):
        # garbage_type, area_code, expected
        self.parameters_type_area = [
        # 日時は各地域ごとに調整していくつか試す。
        # 3/19の段階では、次の燃えるゴミの日は3/22なのでこちらを指定
            ("burnable", "natsume", f"3月の23日がburnableを捨てる日だよ！時間帯はnightだよ"),
            ("non_burnable", "natsume", f"3月の18日がnon_burnableを捨てる日だよ！"), 
        ]

    # fixtures
    # End

    def test_get_next_trash_day_of(self):
        # garbage_type, area_code
        for garbage_type, area_code, expected in self.parameters_type_area:
            with self.subTest():
                self.assertEqual(
                    expected, 
                    get_next_trash_day_of(garbage_type, area_code)
                    )
    

    