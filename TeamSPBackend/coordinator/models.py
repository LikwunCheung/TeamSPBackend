# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Coordinator(models.Model):

    coordinator_id = models.AutoField(verbose_name='id', primary_key=True)
    coordinator_name = models.CharField(max_length=50, blank=False, null=True)
    email = models.CharField(max_length=50, blank=False, null=False)
    join_date = models.BigIntegerField(max_length=20, blank=False, null=False)
    status = models.IntegerField(max_length=2, blank=False, null=False)

    class Meta:
        db_table = 'coordinator'
