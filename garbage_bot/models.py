from django.db import models



class Area(models.Model):
    # TODO: develop the data model.
    # property list
    #   - area_id:
    #   - area_detail: 番地詳細
    area_id = models.IntegerField(primary_key=True)
    town_name = models.CharField(max_length=64, null=True)
    district_name = models.CharField(max_length=64, null=True)
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

    def __str__(self):
        return f"{self.garbage_type} , {self.area_id}"


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
    area_candidates = models.JSONField(null=True, default=dict)
    # 追加したい属性が発生した場合、こちらのカラムで対応する
    optional = models.JSONField(null=True)
    

    uuid = models.CharField(max_length=64, null=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = ["updated_at"]
    def __str__(self):
        return f"{self.uuid} / {self.state} / {str(self.created_at)}"
