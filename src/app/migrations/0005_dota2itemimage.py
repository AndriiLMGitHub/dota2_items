# Generated by Django 3.2.23 on 2024-04-27 15:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20240427_1159'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dota2ItemImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.FileField(upload_to='images/')),
                ('item_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='app.dota2item')),
            ],
        ),
    ]