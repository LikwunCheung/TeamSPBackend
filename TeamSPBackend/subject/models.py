# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from TeamSPBackend.account.models import User

class Subject(models.Model):

    subject_id = models.IntegerField(max_length=10, blank=False, null=False, db_index=True)
    subject_code = models.CharField(max_length=50, blank=False, null=False)
    subject_name = models.CharField(max_length=50, blank=False, null=False)
    coordinator_id = models.ForeignKey(User)
    supervisors = models.ManyToManyField(User)
    # projects = models.ForeignKey(Project)
    status = models.BooleanField(blank=False)

    class Meta:
        db_table = 'subject'


