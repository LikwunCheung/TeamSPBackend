from django.db import models

# Create your models here.
class Account(models.Model):
    accountId = models.CharField(max_length=30, primary_key=True)
    username = models.CharField(max_length=30, unique= True)
    email = models.EmailField(max_length=254, unique = True)
    password = models.CharField(max_length=128)

    class Meta:
        db_table = 'account'
    def __str__(self):
        return self.username

class User(models.Model):
    # id = models.OneToOneField(Account, to_field='id', on_delete= models.CASCADE,primary_key=True)
    accountId = models.CharField(max_length=30, primary_key=True)
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30,null=True)
    last_name  = models.CharField(max_length = 30,null=True)
    role = models.IntegerField(null=True) # 1:supervisor 2:coordinator

    class Meta:
        db_table = 'user'
    def __str__(self):
        return self.username
