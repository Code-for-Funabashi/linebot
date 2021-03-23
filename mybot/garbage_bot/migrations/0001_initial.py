# Generated by Django 3.1.5 on 2021-03-23 01:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('area_id', models.IntegerField(primary_key=True, serialize=False)),
                ('area_name', models.CharField(max_length=15, null=True)),
                ('area_name_capital', models.CharField(max_length=2)),
                ('area_detail', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='GarbageType',
            fields=[
                ('garbage_type', models.IntegerField(primary_key=True, serialize=False)),
                ('garbage_name', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Remind',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.CharField(max_length=64)),
                ('when2push', models.DateField(auto_now=True)),
                ('garbage_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='garbage_bot.garbagetype')),
            ],
        ),
        migrations.CreateModel(
            name='CollectDay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekday_info', models.IntegerField()),
                ('nth_week', models.IntegerField()),
                ('day_or_night', models.IntegerField()),
                ('area_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='garbage_bot.area')),
                ('garbage_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='garbage_bot.garbagetype')),
            ],
        ),
    ]