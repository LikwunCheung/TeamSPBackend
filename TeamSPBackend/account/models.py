from django.db import models

# Create your models here.
from TeamSPBackend.common.choices import Status, Roles


class Account(models.Model):
    account_id = models.AutoField(verbose_name='id', primary_key=True)
    username = models.CharField(max_length=32, unique=True)
    email = models.EmailField(max_length=128, unique=True)
    password = models.CharField(max_length=128)
    status = models.IntegerField(choices=Status.StatusChoice.value, blank=False, null=False)
    create_date = models.BigIntegerField(blank=False, null=False)
    update_date = models.BigIntegerField(blank=False, null=False)

    class Meta:
        db_table = 'account'


class User(models.Model):
    user_id = models.AutoField(verbose_name='id', primary_key=True)
    account_id = models.IntegerField(blank=False, null=False, db_index=True)
    sso_id = models.BigIntegerField(blank=False, null=True, db_index=True)
    first_name = models.CharField(max_length=64, blank=False, null=False)
    last_name = models.CharField(max_length=64, blank=False, null=False)
    role = models.IntegerField(choices=Roles.RolesChoice.value, blank=False, null=False)
    status = models.IntegerField(choices=Status.StatusChoice.value, blank=False, null=False)
    create_date = models.BigIntegerField(blank=False, null=False)
    update_date = models.BigIntegerField(blank=False, null=False)

    class Meta:
        db_table = 'user'

    def get_name(self):
        return self.first_name + ' ' + self.last_name
