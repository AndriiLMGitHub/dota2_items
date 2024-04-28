# Generated by Django 3.2.23 on 2024-04-27 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dota2item',
            name='paid',
        ),
        migrations.RemoveField(
            model_name='dota2item',
            name='received',
        ),
        migrations.AddField(
            model_name='dota2item',
            name='amount',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='dota2item',
            name='class_name',
            field=models.CharField(max_length=256, verbose_name='class'),
        ),
        migrations.AlterField(
            model_name='dota2item',
            name='for_who',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='for'),
        ),
    ]