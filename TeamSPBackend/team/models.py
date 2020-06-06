from django.db import models

# Create your models here.

from TeamSPBackend.common.choices import TeamStatus


class Team(models.Model):
    id = models.AutoField(verbose_name='id', primary_key=True)
    name = models.CharField(max_length=45, null=True)
    description = models.CharField(max_length=1000, null=True)
    create_date = models.DateTimeField(blank=False, null=False,auto_now_add=True)
    expired = models.IntegerField(max_length=2, choices=TeamStatus.TeamStatusChoice.value, blank=False, null=False)
    supervisor_id = models.ForeignKey('User', on_delete=models.CASCADE)

    class Meta:
        db_table = 'team'
