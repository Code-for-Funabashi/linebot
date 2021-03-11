from django.db import models

# Create your models here.


# 町名(頭文字)/町名.1/可燃/可燃.1/不燃/資源/ペット/有価物/番地詳細

class Location(models.Model):
    # TODO: develop the data model.
    # property list
    #   - area_id
    #   - area_name
    #   - 
    #   -
    #   -
    pass

class Location2Day(models.Model):
    # TODO: develop the data model.
    # many2many
    # property list
    #   - area_id
    #   - garbage_type
    #   - 
    #   -
    #   -
    pass

class GarbageType(models.Model):
    # TODO: develop the data model.
    # 可燃 / 不燃 / 資源 / ペット / 有価物
    # property list
    #   - garbage_type
    #   - garbage_name
    pass
