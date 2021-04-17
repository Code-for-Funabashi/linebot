from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _

from django.db.utils import IntegrityError

class GarbageBotConfig(AppConfig):
    name = 'garbage_bot'
    def ready(self):
        post_migrate.connect(setup_data, sender=self)

def make_area_records(row):
    from garbage_bot.models import Area
    return Area(
        area_id=row["index"]+1,
        address_name=row["address_name"],
        district_name=row["district_name"],
        town_name=row["town_name"]
        )


def setup_data(sender, **kwargs):
    """
    django appをサーバに立ち上げるタイミングで船橋のゴミ収集情報をDBに立ち上げる
    # docker-compose exec -T web python manage.py migrate
    """
    from django.contrib.sites.models import Site
    import pandas as pd
    from garbage_bot.models import Area, GarbageType, CollectDay
    from garbage_bot.utils import get_json

    
    # import pdb;pdb.set_trace()
    try:
        # Area creation.
        area_df = pd.read_csv("/code/data/area_df.csv")
        area_objects = area_df.apply(make_area_records, axis=1).to_list()
        Area.objects.bulk_create(area_objects)
    except IntegrityError as e:
        print(f"Error for Area: {e}")
        pass
    
    try:
        # GarbageType creation.
        GarbageTypeList = ["burnable",
                        "non_burnable",
                        "resources",
                        "valuables",]
        GarbageType.objects.bulk_create([GarbageType(garbage_type=idx+1,garbage_name=type_)
                                            for idx, type_ in enumerate(GarbageTypeList)])
    except IntegrityError as e:
        print(f"Error for GarbageType: {e}")
        pass
    try:
        # CollectDay creation.
        sample_df = pd.read_csv("/code/data/sample_df.csv")
        obj_list = sample_df.apply(get_json, axis=1).sum()
        CollectDay.objects.bulk_create([CollectDay(**obj) for obj in obj_list])
    except IntegrityError as e:
        print(f"Error for CollectDay: {e}")
        pass

