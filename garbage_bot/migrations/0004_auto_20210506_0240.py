# Generated by Django 3.1.5 on 2021-05-05 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('garbage_bot', '0003_auto_20210424_1458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='context',
            name='area_candidates',
            field=models.JSONField(default=dict, null=True),
        ),
    ]
