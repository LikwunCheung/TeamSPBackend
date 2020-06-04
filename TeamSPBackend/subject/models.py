from django.db import models


class Subject(models.Model):

    id = models.AutoField(primary_key=True)
    subject_id = models.IntegerField(
        max_length=20, blank=False, null=False, db_index=True, unique=True, primary_key=True)
    name = models.CharField(max_length=128, blank=False, null=False)
    create_date = models.BigIntegerField(
        max_length=20, blank=False, null=False)
    coordinator_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'subject'
