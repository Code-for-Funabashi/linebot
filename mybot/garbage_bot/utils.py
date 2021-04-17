from django.db import models

def get_json(row):
    out_list = []
    for garbage_type in range(1, 4):
        
        # town_name = row["town_name"]
        # district_name = row["district_name"]
        
        nth_week = -1 # 不燃ごみのみ利用する。他のごみは毎週収集する
        day_or_night = -1 # 昼夜の指定がされているのは可燃ごみだけ
        
        # sample_df indexをarea_idにしているので　name propertyで取得
        area_id = row.name
        
        district_info = row[DISTRICT_COL]
        if garbage_type == 1:
            day_or_night = row.iloc[DAY_NIGHT_COLUMN]
            weekday_info = row.iloc[BURNABLE_WD]
            
        elif garbage_type == 2: # non_burnable
            nth_week = row.iloc[8]
            weekday_info = row.iloc[9]
            
        elif garbage_type == 3: # resources / 資源
            weekday_info = row.iloc[RESOURCE]
            
        elif garbage_type == 4: # 有価物
            weekday_info = row.iloc[VALUABLES]

        out_list.append({
            "area_id": area_id,
            # "town_name": town_name,
            # "district_name": district_name,
            "garbage_type": garbage_type,
            "day_or_night":day_or_night,
            "nth_week":nth_week,
            "weekday_info":weekday_info,
            # "district_info": "none" if district_info else district_info
        })
    return out_list


# def get_context_or_none(Model: models.Model, user_id):

#     try:
#         context: Context = Context.objects.filter(uuid=user_id).latest()
#         actual = get_day_to_collect(context)
#     except ObjectDoesNotExist:
#         actual = None


