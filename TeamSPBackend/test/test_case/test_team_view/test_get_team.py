from django.test import TestCase, Client
from django.http import HttpRequest

from TeamSPBackend.common.choices import Roles
from TeamSPBackend.team.models import Team, TeamMember, Student
from TeamSPBackend.api.views import team
from TeamSPBackend.test.utils import login_helpers, object_creation_helpers
import names


class GetTeamTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        object_creation_helpers.createGenericAdmin()

    def setUp(self):
        login_helpers.login(self.client)
        session = self.client.session
        # Set up a test team object
        team_data = {
            "name": "test_swen90013_2020_sp",
            "subject_code": '123',
            "supervisor_id": 2,
            "secondary_supervisor_id": 3,
            "year": "2020",
            "create_date": "01012020",
            "project_name": "sp",
            "sprint_start_0": "1",
            "sprint_end_0": "1",
            "sprint_start_1": "1",
            "sprint_end_1": "1",
            "sprint_start_2": "1",
            "sprint_end_2": "1",
            "sprint_start_3": "1",
            "sprint_end_3": "1",
            "sprint_start_4": "1",
            "sprint_end_4": "1",
        }
        team = Team(name=team_data["name"],
                    subject_code=team_data["subject_code"],
                    supervisor_id=team_data["supervisor_id"],
                    secondary_supervisor_id=team_data["secondary_supervisor_id"],
                    year=team_data["year"],
                    create_date=team_data["create_date"],
                    project_name=team_data["project_name"],
                    sprint_start_0=team_data["sprint_start_0"],
                    sprint_end_0=team_data["sprint_end_0"],
                    sprint_start_1=team_data["sprint_start_1"],
                    sprint_end_1=team_data["sprint_end_1"],
                    sprint_start_2=team_data["sprint_start_2"],
                    sprint_end_2=team_data["sprint_end_2"],
                    sprint_start_3=team_data["sprint_start_3"],
                    sprint_end_3=team_data["sprint_end_3"],
                    sprint_start_4=team_data["sprint_start_4"],
                    sprint_end_4=team_data["sprint_end_4"],
                    )
        team.save()

        self.team = Team.objects.get(name=team_data["name"])

        # Set up team member and student objects
        member_1_data = {
            "student_id": 1,
            "team_id": 1
        }
        member_2_data = {
            "student_id": 2,
            "team_id": 1
        }
        member_1 = TeamMember(student_id=member_1_data["student_id"],
                              team_id=member_1_data["team_id"])
        member_2 = TeamMember(student_id=member_2_data["student_id"],
                              team_id=member_2_data["team_id"])
        member_1.save()
        member_2.save()

        self.members = [member_1_data, member_2_data]

        student_1_data = {
            "fullname": "student1",
            "email": "student1@gmail.com",
            "git_name": "student1",
            "slack_email": "student1@gmail.com"
        }
        student_2_data = {
            "fullname": "student2",
            "email": "student2@gmail.com",
            "git_name": "student2",
            "slack_email": "student2@gmail.com"
        }
        student_1 = Student(fullname=student_1_data["fullname"],
                            email=student_1_data["email"],
                            git_name=student_1_data["git_name"],
                            slack_email=student_1_data["slack_email"])
        student_2 = Student(fullname=student_2_data["fullname"],
                            email=student_2_data["email"],
                            git_name=student_2_data["git_name"],
                            slack_email=student_2_data["slack_email"])
        student_1.save()
        student_2.save()

        self.students = [student_1_data, student_2_data]

    def test_get_team_members_success(self):
        """
        Tests the success scenario for function get_team_members
        for the API: Get 'team/<int:id>'
        """
        session = self.client.session
        # Set up supervisor
        first_name = names.get_first_name()
        last_name = names.get_last_name()
        session["supervisor_1_details"] = {
            "first_name": first_name,
            "last_name": last_name,
            "email": first_name + last_name + "gmail.com"
        }
        session.save()
        object_creation_helpers.createUser(Roles.supervisor, session["supervisor_1_details"])

        # Set up secondary supervisor
        first_name = names.get_first_name()
        last_name = names.get_last_name()
        session["supervisor_2_details"] = {
            "first_name": first_name,
            "last_name": last_name,
            "email": first_name + last_name + "gmail.com"
        }
        session.save()
        object_creation_helpers.createUser(Roles.supervisor, session["supervisor_2_details"])

        response = self.client.get('/api/v1/team/1')
        expected_data = {
            'supervisor': {
                'supervisor_id': 2,
                'supervisor_first_name': session["supervisor_1_details"]["first_name"],
                'supervisor_last_name': session["supervisor_1_details"]["last_name"],
                'email': session["supervisor_1_details"]["email"]
            },
            'secondary_supervisor': {
                'secondary_supervisor_id': 3,
                'secondary_supervisor_first_name': session["supervisor_2_details"]["first_name"],
                'secondary_supervisor_last_name': session["supervisor_2_details"]["last_name"],
                'email': session["supervisor_2_details"]["email"]
            },
            'team_members': [
                {
                    'student_id': self.members[0]["student_id"],
                    'fullname': self.students[0]["fullname"],
                    'email': self.students[0]["email"]
                },
                {
                    'student_id': self.members[1]["student_id"],
                    'fullname': self.students[1]["fullname"],
                    'email': self.students[1]["email"]
                }
            ]
        }
        self.assertEqual(response.json()["data"], expected_data, 'Get team members data is not as expected.')

    def test_get_team_members_supervisor_failure(self):
        """
        Tests the failure scenario for function get_team_members when supervisor does not exist
        for the API: Get 'team/<int:id>'
        """
        response = self.client.get('/api/v1/team/1')
        session = self.client.session
        self.assertEqual(response.json()['data']['supervisor'], "supervisor not exist", "supervisor exists or response data is incorrect")

    def test_get_team_members_secondary_supervisor_failure(self):
        """
        Tests the failure scenario for function get_team_members when secondary supervisor does not exist
        for the API: Get 'team/<int:id>'
        """
        response = self.client.get('/api/v1/team/1')
        session = self.client.session
        self.assertEqual(response.json()['data']['secondary_supervisor'], "secondary_supervisor not exist", "secondary supervisor exists or response data is incorrect")
