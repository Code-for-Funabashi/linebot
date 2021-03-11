from django.db import models

# Create your models here.


# 町名(頭文字)/町名.1/可燃/可燃.1/不燃/資源/ペット/有価物/番地詳細

class Area(models.Model):
    # TODO: develop the data model.
    # property list
    #   - area_id:
    #   - area_name: 町名
    #   - area_name_capital: 町名の頭文字

    #   - area_detail: 番地詳細
    area_id = models.PrimaryKey()
    area_name = models.CharField(max_length=15, null=True)
    area_name_capital = models.CharField(max_length=2, null=False)
    area_detail = models.CharField(max_length=30, null=False)

class GarbageType(models.Model):
    # TODO: develop the data model.
    # 可燃(週に2回) / 不燃 / 資源 / ペット / 有価物
    # property list
    #   - garbage_type
    #   - garbage_name
    garbage_type = models.IntegerField(primary_key=True)
    garbage_name = models.CharField(max_length=10, null=False)

    pass


class Area2Day(models.Model):
    # TODO: develop the data model.
    # many2many
    # property list
    #   - area_id
    #   - garbage_type
    #   - day
    # 不燃は月一
    # collection_schedule: 第何週にゴミ回収があるのかの情報をいれる
    # TODO: feature/model_dev
    # collection_schedule & weekday_info
    # 複数ある収集日をどう扱うか、要検討
    area_id = models.ForeignKey(Area)
    garbage_type = models.ForeignKey(GarbageType)
    weekday_info = models.IntegerField()

    collection_schedule = models.IntegerField(default=-1)
    optional = CharField(max_length=10, null=False)

