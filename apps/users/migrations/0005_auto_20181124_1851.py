# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-24 18:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20181123_2147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailverifyrecord',
            name='code',
            field=models.CharField(max_length=50, verbose_name='验证码'),
        ),
    ]
