from django.test import TestCase, Client
from django.http import HttpRequest
import sys
import hashlib

from TeamSPBackend.team.models import Team
from TeamSPBackend.api.views import team
from TeamSPBackend.account.models import Account
from TeamSPBackend.test.helper import loginHelper
from TeamSPBackend.common.config import SALT

sys.path.append('/Users/keri/git/TeamSPBackend/TeamSPBackend' + '/..')


class CreateTeamTestCase(TestCase):

    def test_create_team(self):
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
        req.POST = team_data
        response = team.create_team(req)

        self.assertEqual(response.status_code, 200, "response code is not 200")

        created_team = Team.objects.get(name=team_data["name"])
        self.assertIsNotNone(created_team, "team is not created")


if __name__ == '__main__':
    TestCase.main()
