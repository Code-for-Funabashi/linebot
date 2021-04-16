from django.apps import AppConfig
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _

from .utils import get_json

class GarbageBotConfig(AppConfig):
    name = 'garbage_bot'
    def ready(self):
        post_migrate.connect(setup_data, sender=self)

def make_area_records(row):
    return Area(
        address_name=row["address_name"],
        district_name=row["district_name"],
        town_name=row["town_name"]
        )


def setup_data(sender, **kwargs):
    """
    django appをサーバに立ち上げるタイミングで船橋のゴミ収集情報をDBに立ち上げる
    """
    from django.contrib.sites.models import Site
    import pandas as pd
    from models import Area

    # Area creation.
    area_df = pd.read_csv("../area_df.csv")
    area_objects = area_df.apply(make_area_records, axis=1).to_list()
    Area.objects.bulk_create(area_objects)
    # bulk_createで一括saveできるのか検証中

    # GarbageType creation.
    GarbageTypeList = ["burnable",
                    "non_burnable",
                    "resources",
                    "valuables",]
    GarbageType.objects.bulk_create([GarbageType(garbage_type=idx, garbage_name=type_)
                                        for idx, type_ in enumerate(GarbageTypeList)])

    # CollectDay creation.
    obj_list = sample_df.apply(get_json, axis=1).sum()
    CollectDay.objects.bulk_create([CollectDay(obj) for obj in obj_list])

