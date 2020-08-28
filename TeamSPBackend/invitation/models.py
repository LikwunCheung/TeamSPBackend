# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Invitation(models.Model):

    invitation_id = models.AutoField(db_column='id', primary_key=True)
    key = models.CharField(max_length=128, blank=False, null=False, db_index=True, unique=True)
    first_name = models.CharField(max_length=50, blank=False, null=True)
    last_name = models.CharField(max_length=50, blank=False, null=True)
    email = models.CharField(max_length=50, blank=False, null=False)
    operator = models.IntegerField(blank=False, null=False)
    create_date = models.BigIntegerField(blank=False, null=False)
    send_date = models.BigIntegerField(blank=False, null=True)
    accept_reject_date = models.BigIntegerField(blank=False, null=True)
    expired = models.BigIntegerField(blank=False, null=False, db_index=True)
    status = models.IntegerField(blank=False, null=False)

    class Meta:
        db_table = 'invitation'

    def get_name(self):
        return self.first_name + ' ' + self.last_name
