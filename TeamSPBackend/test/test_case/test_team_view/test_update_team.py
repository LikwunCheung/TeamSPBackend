from django.test import TestCase, Client
from django.http import HttpRequest
#  import sys
import hashlib

from TeamSPBackend.team.models import Team
from TeamSPBackend.api.views import team
from TeamSPBackend.account.models import Account
from TeamSPBackend.common.config import SALT

#  sys.path.append('/Users/keri/git/TeamSPBackend/TeamSPBackend' + '/..')


class UpdateTeamTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        team_data = {
            "name": "test_swen90013_2020_sp",
            "description": "this is a team created for testing",
            "subject_id": 123,
            "supervisor_id": 2,
            "secondary_supervisor_id": 3,
            "year": "2020",
            "create_date": "01012020",
            "expired": 2222,
            "project_name": "sp"
        }
        req = HttpRequest()
        req.body = team_data
        response = team.create_team(req)

        self.team = Team.objects.get(name=team_data["name"])

    def test_update_team_description_supervisorid_secsupervisorid(self):
        new_team_data = {
            "description": "new description",
            "supervisor_id": 5,
            "secondary_supervisor_id": 6
        }
        req = HttpRequest()
        req.body = new_team_data
        team.update_team(req, self.team["team_id"])

        updated_team = Team.objects.get(name=self.team["name"])
        self.assertEqual(
            updated_team["name"], self.team_data["name"], "team names are not equal")
        self.assertNotEqual(
            updated_team["description"], "this is a team created for testing", "description is not updated")
        self.assertEqual(
            updated_team["description"], "new description", "description is still not updated")
        self.assertEqual(updated_team["supervisor_id"],
                         5, "supervisor_id not updated")
        self.assertEqual(
            updated_team["secondary_supervisor_id"], 6, "secondary_supervisor_id not updated")
