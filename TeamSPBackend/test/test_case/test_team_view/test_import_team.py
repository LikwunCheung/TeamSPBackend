from django.test import TestCase, Client
from django.http import HttpRequest

from TeamSPBackend.team.models import Team
from TeamSPBackend.api.views import team
from TeamSPBackend.test.utils import login_helpers, object_creation_helpers


class ImportTeamTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        object_creation_helpers.createGenericAdmin()

    def setUp(self):
        login_helpers.login(self.client)
        # Set up atlassian credentials
        session = self.client.session
        session["user"]["atl_username"] = "yho4"
        session["user"]["atl_password"] = "mil1maci"
        session.save()

    def test_import_team_success_team_is_saved(self):
        """
        Tests the function for the API: Post 'team'
        """
        # Set up team data to import
        team_body = {
            "team": "swen90013-2020-ce",
            "subject": "swen90013",
            "year": "2020",
            "project": "ce"
        }
        print(str(self.client.post('/api/v1/team', data=team_body, content_type="application/json").json()))
        teams = Team.objects.all()
        print(str(teams))
        imported_team = Team.objects.get(name="swen90013-2020-ce")
        imported_team_dict = {
            "team": imported_team.name,
            "subject": imported_team.subject_code,
            "year": imported_team.year,
            "project": imported_team.project_name
        }
        self.assertDictEqual(team_body, imported_team_dict, "Input body and imported team data is not equal.")


if __name__ == '__main__':
    TestCase.main()
