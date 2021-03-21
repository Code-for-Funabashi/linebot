from django.apps import AppConfig
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _



class GarbageBotConfig(AppConfig):
    name = 'garbage_bot'
    def ready(self):
        post_migrate.connect(setup_dummy_social_apps, sender=self)




def setup_Location_data(sender, **kwargs):
    """
    django appをサーバに立ち上げるタイミングで船橋のゴミ収集情報をDBに立ち上げる
    """
    from django.contrib.sites.models import Site
    import pandas as pd
    from models import Area

    site = Site.objects.get_current()
    # 
    area_name = df["町名.1"]
    area_name_capital = df["町名"]
    area_detail = df["番地詳細"]
    # df.apply(lambda row: )
    Area.objects.create(
        area_name=area_name,
        area_name_capital=area_name_capital,
        area_detail=area_detail,
    )
    # bulk_createを用いる。
    

    # app = SocialApp.objects.create(
    #     provider=provider.id,
    #     secret='secret',
    #     client_id='client-id',
    #     name='Dummy %s app' % provider.id)
    app.sites.add(site)
