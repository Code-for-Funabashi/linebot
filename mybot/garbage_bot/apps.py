from django.apps import AppConfig
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _



class GarbageBotConfig(AppConfig):
    name = 'garbage_bot'
    def ready(self):
        post_migrate.connect(setup_dummy_social_apps, sender=self)


# データテーブル
# from urllib import request
# import ssl
# # , flavor="bs4"
# url="https://www.city.funabashi.lg.jp/kurashi/gomi/001/p001523.html"
# context = ssl._create_unverified_context()
# response = request.urlopen(url, context=context)
# html = response.read()
# collectionDayPerArea = pd.read_html(html)
# from IPython.display import display
# for i in collectionDayPerArea:
#     display(i)



def setup_Location_data(sender, **kwargs):
    """
    django appをサーバに立ち上げるタイミングで船橋のゴミ収集情報をDBに立ち上げる
    """
    from django.contrib.sites.models import Site
    from models import Location

    site = Site.objects.get_current()
    # 

    app = SocialApp.objects.create(
        provider=provider.id,
        secret='secret',
        client_id='client-id',
        name='Dummy %s app' % provider.id)
    app.sites.add(site)
