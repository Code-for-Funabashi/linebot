from django.test import TestCase
import views
# Create your tests here.

class Garbage_BotTestCase(TestCase):
    def setUp(self):
        # garbage_type, area_code, expected
        parameters_type_area = [
        # 日時は各地域ごとに調整していくつか試す。
        # 3/19の段階では、次の燃えるゴミの日は3/22なのでこちらを指定
            ("burnable", "natsume", f"3月の22日がburnableを捨てる日だよ！"), 
        ]

    # fixtures
    # End

    def test_get_next_trash_day_of(self):
        # garbage_type, area_code
        for garbage_type, area_code, expected in parameters_type_area:
            with self.subTest():
                self.assertEqual(
                    expected, 
                    views.get_next_trash_day_of(garbage_type, area_code)
                    )
    

    