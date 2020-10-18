from django.db import models
# Create your models here.


class SlackTeam(models.Model):
    id = models.AutoField(primary_key=True)
    team_id = models.IntegerField()
    channel_name = models.CharField(max_length=50)
    message_num = models.IntegerField()
    sprint_num = models.IntegerField()
    time = models.BigIntegerField()

    class Meta:
        db_table = 'slack_team'

