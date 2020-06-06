# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from TeamSPBackend.common.choices import Status


class Subject(models.Model):

    subject_id = models.AutoField(verbose_name='id', primary_key=True)
    subject_code = models.CharField(verbose_name='subject_id', max_length=20, blank=False, null=True, unique=True)
    name = models.CharField(max_length=128, blank=False, null=True)
    coordinator_id = models.IntegerField(blank=False, null=False)
    create_date = models.BigIntegerField(blank=False, null=False)
    status = models.IntegerField(choices=Status.StatusChoice.value, blank=False, null=False)

    class Meta:
        db_table = 'subject'
