from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _
import csv

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

    from garbage_bot.models import Area, GarbageType, CollectDay
    from garbage_bot.utils import get_json

    
    # import pdb;pdb.set_trace()
    try:
        # Area creation.
        area_objects = []
        with open("/code/data/area_df.csv", "r+") as f:
            lines = csv.reader(f)
            head = next(lines)
            print(head)
            # import pdb; pdb.set_trace()
            for l_ in lines:
                # l_ = [el if el else None for el in l.strip().split(",")]
                # print(l_)
                row=dict(
                    index=int(l_[0]),
                    town_name=l_[1],
                    district_name=l_[2],
                    address_name=l_[3],
                )
                area_objects.append(make_area_records(row))
        Area.objects.bulk_create(area_objects)
    except IntegrityError as e:
        print(f"Error for Area: {e}")
        pass
    except Exception as e:

        print(e)
        import pdb; pdb.set_trace()

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
        obj_list = []

        with open("/code/data/sample_df.csv", "r+") as f:
            lines = csv.reader(f)
            next(lines)
            for i, l in enumerate(lines):
                # ['あ', '旭町1丁目', '0,3', '1', '2木', '2', '2.0', '', '2', '3', '旭町', '1丁目']
                obj_list.extend(get_json(l, i))
            

        CollectDay.objects.bulk_create([CollectDay(**obj) for obj in obj_list])
    except IntegrityError as e:
        print(f"Error for CollectDay: {e}")
        pass

