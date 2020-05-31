# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Subject(models.Model):

    subject_id = models.AutoField(verbose_name='id', primary_key=True)
    subject_code = models.CharField(max_length=50, blank=False, null=False)
    subject_name = models.CharField(max_length=50, blank=False, null=False)
    create_date = models.BigIntegerField(max_length=20, blank=False, null=False)
    coordinator_id = models.CharField(max_length=50, blank=True, null=True)
    status = models.BooleanField(blank=False)

    class Meta:
        db_table = 'subject'


