# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Project(models.Model):

    project_id = models.AutoField(verbose_name='id', primary_key=True)
    project_name = models.CharField(max_length=50, blank=False, null=False)
    create_date = models.BigIntegerField(max_length=20, blank=False, null=False)
    start_date = models.BigIntegerField(max_length=20, blank=False, null=False)
    end_date = models.BigIntegerField(max_length=20, blank=False, null=False)
    status = models.BooleanField(blank=False)

    class Meta:
        db_table = 'project'


