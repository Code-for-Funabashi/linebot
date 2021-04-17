from django.db import models

# Create your models here.


sample_natsume = {"burnable":"-1/1,2/night",
                "non_burnable":"3/3/",  "Resources・PET" : "-1/2/", "valuables" : "-1/2/"}


# 町名(頭文字)/町名.1/可燃/可燃.1/不燃/資源/ペット/有価物/番地詳細

class Area(models.Model):
    # TODO: develop the data model.
    # property list
    #   - area_id:
    #   - area_name: 町名
    #   - area_name_capital: 町名の頭文字

    #   - area_detail: 番地詳細
    area_id = models.IntegerField(primary_key=True)
    # 
    town_name = models.CharField(max_length=15, null=True)
    district_name = models.CharField(max_length=15, null=True)
    address_name = models.CharField(max_length=64, null=True)

    def __str__(self):
        return self.town_name +"/"+ self.district_name +"/"+ self.address_name
class GarbageType(models.Model):
    # TODO: develop the data model.
    # 可燃(週に2回) / 不燃 / 資源 / ペット / 有価物
    # property list
    #   - garbage_type
    #   - garbage_name
    garbage_type = models.IntegerField(primary_key=True)
    garbage_name = models.CharField(max_length=20, null=False)

    def __str__(self):
        return self.garbage_name


class CollectDay(models.Model):
    # TODO: develop the data model.
    # many2many
    # property list
    #   - area_id
    #   - garbage_type
    #   - day
    area_id = models.ForeignKey(Area, on_delete=models.CASCADE)
    garbage_type = models.ForeignKey(GarbageType, on_delete=models.CASCADE)
    weekday_info = models.CharField(max_length=10, null=False)
    nth_week = models.IntegerField()
    day_or_night = models.IntegerField()
    # models.JSONField()


class Remind(models.Model):
    uuid = models.CharField(max_length=64, null=False)
    when2push = models.DateField(auto_now=True)
    garbage_type = models.ForeignKey(GarbageType, on_delete=models.CASCADE)


# 
# class UserRecentHistory(models.Model):
#     uuid = models.CharField(max_length=64, null=False)
#     created_at = models.DateTimeField(auto_now=True)
#     updated_at = models.DateTimeField(auto_now=True)

class Context(models.Model):
    session_id = models.CharField(max_length=64, null=False)
    state = models.IntegerField() # 各セッション毎に、どこまでユーザとの会話が進んでいるか？
    garbage_type = models.ForeignKey(GarbageType, 
            on_delete=models.CASCADE, 
            null=True,
            )
    # area_id = models.ForeignKey(Area, on_delete=models.CASCADE)
    area_candidates = models.JSONField(null=True)
    # 追加したい属性が発生した場合、こちらのカラムで対応する
    optional = models.JSONField(null=True)
    

    uuid = models.CharField(max_length=64, null=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = ["updated_at"]