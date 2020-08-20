import csv
import codecs
from TeamSPBackend.team.models import Team, TeamMember


def read_csv(file, subject_id: int):
    with file as csv_file:
        rows = []
        data = csv.reader(codecs.iterdecode(csv_file, 'utf-8'))
        for row in data:
            rows.append(row)
            print(row)

        for row in rows:
            name = row[0]
            description = row[1]
            supervisor_id = row[2]
            create_date = row[3]
            expired = row[4]
            project_name = row[5]
            student_ids = row[6]
            list_students_ids = student_ids.split(",")
            print(name, description, subject_id, supervisor_id, create_date, expired, project_name)
            team = Team(name=name, description=description, subject_id=subject_id, supervisor_id=supervisor_id,
                        create_date=create_date, expired=expired,  project_name=project_name)

            team.save()
            print(team)
            for student_id in list_students_ids:
                team_member = TeamMember(team_id=team.team_id, student_id=student_id)
                team_member.save()


