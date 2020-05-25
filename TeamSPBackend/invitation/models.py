# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from TeamSPBackend.common.choices import InvitationStatus


class Invitation(models.Model):

    invitation_id = models.AutoField(verbose_name='id', primary_key=True)
    subject_id = models.IntegerField(max_length=10, blank=False, null=False, db_index=True)
    supervisor_id = models.IntegerField(max_length=10, blank=False, null=True)
    key = models.CharField(max_length=128, blank=False, null=False, db_index=True, unique=True)
    first_name = models.CharField(max_length=50, blank=False, null=True)
    last_name = models.CharField(max_length=50, blank=False, null=True)
    email = models.CharField(max_length=50, blank=False, null=False)
    operator = models.IntegerField(max_length=10, blank=False, null=False)
    create_date = models.BigIntegerField(max_length=20, blank=False, null=False)
    send_date = models.BigIntegerField(max_length=20, blank=False, null=True)
    accept_reject_date = models.BigIntegerField(max_length=20, blank=False, null=True)
    expired = models.BigIntegerField(max_length=20, blank=False, null=False, db_index=True)
    status = models.IntegerField(max_length=2, choices=InvitationStatus.InvitationStatusChoice.value, blank=False, null=False)

    class Meta:
        db_table = 'invitation'
