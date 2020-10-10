from django.test import TestCase, Client
from django.http import HttpRequest
#  import sys
import hashlib

from TeamSPBackend.team.models import Team
from TeamSPBackend.api.views import team
from TeamSPBackend.account.models import Account, User
from TeamSPBackend.common.config import SALT
from TeamSPBackend.common.choices import Status
from TeamSPBackend.common.utils import mills_timestamp
from TeamSPBackend.test.utils import login_helpers, object_creation_helpers

#  sys.path.append('/Users/keri/git/TeamSPBackend/TeamSPBackend' + '/..')


class CreateTeamTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        object_creation_helpers.createGenericAdmin()

    def setUp(self):
        login_helpers.login(self.client)

    def test_create_team_success(self):

        # Create team
        team_data = {
            "team_name": "swen90013-2020-sp"
        }
        response = self.client.post('/api/v1/team', data=team_data, content_type="application/json")
        print("response is " + str(response.json()))

        for team in Team.objects.all():
            print("team is " + team.name)
        #  createdTeam = Team.objects.get(name="test_swen90013_2020_sp")
        #  correctTeamInfo = ["this is a team created for testing", "SWEN90013", 2, 3, "2020", "01012020", "sp"]
        #  createdTeamInfo = [createdTeam.description, createdTeam.subject_code, createdTeam.supervisor_id,
            #  createdTeam.secondary_supervisor_id, createdTeam.year, createdTeam.create_date, createdTeam.project_name]
        #  self.assertEqual(correctTeamInfo, createdTeamInfo, "team is not created successfully")


if __name__ == '__main__':
    TestCase.main()
