from django.test import TestCase, Client
from django.http import HttpRequest
#  import sys
import hashlib

from TeamSPBackend.team.models import Team
from TeamSPBackend.api.views import team
from TeamSPBackend.test.utils import login_helpers, object_creation_helpers

#  sys.path.append('/Users/keri/git/TeamSPBackend/TeamSPBackend' + '/..')


class UpdateTeamTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        object_creation_helpers.createGenericAdmin()

    def setUp(self):
        login_helpers.login(self.client)
        team_data = {
            "name": "test_swen90013_2020_sp",
            "subject_code": '123',
            "supervisor_id": 2,
            "secondary_supervisor_id": 3,
            "year": "2020",
            "create_date": "01012020",
            "project_name": "sp",
            "sprint_start_0": "123456",
            "sprint_end_0": "123456",
            "sprint_start_1": "123456",
            "sprint_end_1": "123456",
            "sprint_start_2": "123456",
            "sprint_end_2": "123456",
            "sprint_start_3": "123456",
            "sprint_end_3": "123456",
            "sprint_start_4": "123456",
            "sprint_end_4": "123456",
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

    def test_update_team_success(self):
        """
        Tests the success scenario for function update_team
        for the API: Post 'team/<int:id>'
        """
        new_team_data = {
            "supervisor_id": 5,
            "secondary_supervisor_id": 7,
        }
        self.client.post('/api/v1/team/1', data=new_team_data, content_type="application/json").json()

        updated_team = Team.objects.get(name=self.team.name)
        updated_team_data = {
            "supervisor_id": updated_team.supervisor_id,
            "secondary_supervisor_id": updated_team.secondary_supervisor_id
        }
        self.assertDictEqual(new_team_data, updated_team_data, "team data is not updated or somehow not equal")

    def test_update_team_failure(self):
        """
        Tests the failure scenario for function update_team
        for the API: Post 'team/<int:id>'
        """
        new_team_data = {
            "supervisor_id": 5,
            "secondary_supervisor_id": 7,
        }
        self.client.post('/api/v1/team/2', data=new_team_data, content_type="application/json").json()
        updated_team = Team.objects.get(name=self.team.name)
        updated_team_data = {
            "supervisor_id": updated_team.supervisor_id,
            "secondary_supervisor_id": updated_team.secondary_supervisor_id
        }
        self.assertNotEqual(new_team_data, updated_team_data, "team data is somehow updated or equal despite wrong team id being inputted")
