from django.db import models
from TeamSPBackend.account.models import Account
# Create your models here.


class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    # student_number = models.IntegerField()
    fullname = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=254, unique=True)

    class Meta:
        db_table = 'student'


class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, unique= True)
    description = models.CharField(max_length=1000)
    subject_id = models.CharField(max_length=30)
    # supervisor = models.ForeignKey('Account',on_delete= models.SET_NULL)
    supervisor_id = models.IntegerField()
    secondary_supervisor_id = models.IntegerField()
    year = models.IntegerField()
    # member = models.ForeignKey('Student',on_delete= models.SET_NULL)
    # member_id = models.IntegerField()
    create_date = models.BigIntegerField(blank=False, null=False)
    # expired = models.BigIntegerField(blank=False, null=False, db_index=True)
    project_name = models.CharField(max_length=30)

    class Meta:
        db_table = 'team'


class TeamMember(models.Model):
    member_id = models.AutoField(primary_key=True)
    student_id = models.IntegerField()
    team_id = models.IntegerField()


    class Meta:
        db_table = 'team_member'

