# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Account(models.Model):

    account_id = models.IntegerField(max_length=10, blank=False, null=False, db_index=True)
    username  = models.CharField(max_length=50, blank=False, null=False)  
    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    email = models.CharField(max_length=50, blank=False, null=False)
    role = models.CharField(max_length=50, blank=False, null=False)
    status = models.BooleanField(blank=False)

    class Meta:
        db_table = 'account'


