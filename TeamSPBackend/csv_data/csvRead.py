import csv
from django.utils.timezone import now
from TeamSPBackend.team.models import Team
filename = "template.csv"
rows = []
colNames = []

with open (filename, 'r') as csvfile:
    data = csv.reader(csvfile)
    colNames = next(data)
    for row in data:
        rows.append(row)

    for row in rows:
        name = row[0]
        description = row[1]
        subject_code  = row[2]
        project_name = row[3]
        start_date = row[4]
        expire_date = row[5]
        supervisor = row[6]
        student_ids = row[7]
        list_students_ids = student_ids.split(",")
        member_names = rows[8]
        list_member_names = member_names.split(",")
        member_emails = rows[8]
        list_member_emails = member_emails.split(",")

        team = Team(name = name, description = description, create_date = int(now().timestamp()), subject_code = subject_code,
                    project_name = project_name, start_date = start_date,
                    expire_date = expire_date, supervisor = supervisor, student_ids = student_ids,
                    member_names = member_names, emails = list_member_emails)
        team.save()