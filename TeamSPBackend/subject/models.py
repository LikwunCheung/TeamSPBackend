# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Subject(models.Model):

    subject_id = models.AutoField(db_column='id', primary_key=True)
    subject_code = models.CharField(db_column='subject_id', max_length=20, blank=False, null=True, unique=True)
    name = models.CharField(max_length=128, blank=False, null=True)
    coordinator_id = models.IntegerField(blank=False, null=False)
    create_date = models.BigIntegerField(blank=False, null=False)
    status = models.IntegerField(blank=False, null=False)

    class Meta:
        db_table = 'subject'
