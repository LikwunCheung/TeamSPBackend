# -*- coding: utf-8 -*-

from django.db import models


class Account(models.Model):

    account_id = models.AutoField(db_column='id', primary_key=True)
    username = models.CharField(max_length=32, unique=True)
    email = models.EmailField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    status = models.IntegerField(blank=False, null=False)
    create_date = models.BigIntegerField(blank=False, null=False)
    update_date = models.BigIntegerField(blank=False, null=False)

    class Meta:
        db_table = 'account'


class User(models.Model):

    user_id = models.AutoField(db_column='id', primary_key=True)
    account_id = models.IntegerField(blank=False, null=False, db_index=True)
    sso_id = models.BigIntegerField(blank=False, null=True, db_index=True)
    username = models.CharField(max_length=32, unique=True, null=False)
    first_name = models.CharField(max_length=64, blank=False, null=False)
    last_name = models.CharField(max_length=64, blank=False, null=False)
    email = models.CharField(max_length=128, null=False)
    atl_username = models.CharField(max_length=128)
    atl_password = models.CharField(max_length=256)
    role = models.IntegerField(blank=False, null=False)
    status = models.IntegerField(blank=False, null=False)
    create_date = models.BigIntegerField(blank=False, null=False)
    update_date = models.BigIntegerField(blank=False, null=False)
    git_username = models.CharField(max_length=128)
    slack_email = models.CharField(max_length=128)

    class Meta:
        db_table = 'user'

    def get_name(self):
        return self.first_name + ' ' + self.last_name
