from django.db import models

# Create your models here.
from TeamSPBackend.common.choices import AccountStatus, Roles


class Account(models.Model):
    # accountId = models.CharField(max_length=30, primary_key=True)
    accountId = models.AutoField(primary_key=True)
    username = models.CharField(max_length=30, unique= True)
    email = models.EmailField(max_length=254, unique = True)
    password = models.CharField(max_length=128)
    status = models.IntegerField(max_length=2, choices=AccountStatus.AccountStatusChoice.value, blank=False, null=False)
    create_date = models.DateTimeField(blank=False, null=False,auto_now_add=True)

    class Meta:
        db_table = 'account'


class User(models.Model):
    # id = models.OneToOneField(Account, to_field='id', on_delete= models.CASCADE,primary_key=True)
    id = models.AutoField(verbose_name='id', primary_key=True)
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30,null=True)
    last_name  = models.CharField(max_length = 30,null=True)
    role = models.IntegerField(null=True, choices=Roles.RolesChoice.value)
    status = models.IntegerField(max_length=2, choices=AccountStatus.AccountStatusChoice.value, blank=False, null=False)
    create_date = models.DateTimeField(blank=False, null=False,auto_now_add=True)

    class Meta:
        db_table = 'user'

