from django.test import TestCase, Client
from django.http import HttpRequest
import sys
import hashlib

from TeamSPBackend.team.models import Team
from TeamSPBackend.api.views import team
from TeamSPBackend.account.models import Account, User
from TeamSPBackend.common.config import SALT
from TeamSPBackend.common.choices import Status
from TeamSPBackend.common.utils import mills_timestamp

sys.path.append('/Users/keri/git/TeamSPBackend/TeamSPBackend' + '/..')


def encrypt(password):
    password = password + SALT
    md5 = hashlib.sha3_256(password.encode()).hexdigest()
    return md5


class CreateTeamTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        # create account
        timestamp = mills_timestamp()
        username = "username"
        password = "password"
        email = "test@gmail.com"
        status = Status.valid.value.key
        create_date = timestamp
        update_date = timestamp
        first_name = "Zach"
        last_name = "Ho"
        role = 0
        md5 = encrypt(password)
        account = Account(username=username, email=email, password=md5,
                          status=status, create_date=create_date, update_date=update_date)
        account.save()

        # create user
        user = User(account_id=account.account_id, username=username, first_name=first_name, last_name=last_name,
                    role=role, status=status, create_date=create_date, update_date=update_date, email=email)
        user.save()

    def test_create_team(self):
        # Login first
        username = "username"
        password = "password"
        credentials = {
            'username': username,
            'password': password
        }

        response = self.client.post('/api/v1/account/login',
                                    data=credentials, content_type="application/json")
        user = User.objects.get(username=username)
        session_data = dict(
            id=user.user_id,
            name=user.get_name(),
            role=user.role,
            is_login=True,
        )
        session = self.client.session
        session['user'] = session_data
        session.save()

        # Create team
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

        response = self.client.post('/api/v1/team', data=team_data)
        print("create team response is " + str(response.json()))
        self.assertEqual(response.status_code, 200, "response code is not 200")

    # def test_create_team(self):
        # team_data = {
        # "name": "test_swen90013_2020_sp",
        # "description": "this is a team created for testing",
        # "subject_id": 123,
        # "supervisor_id": 2,
        # "secondary_supervisor_id": 3,
        # "year": "2020",
        # "create_date": "01012020",
        # "expired": 2222,
        # "project_name": "sp"
        # }
        # req = HttpRequest()
        # req.body = team_data
        # response = team.create_team(req)

        # self.assertEqual(response.status_code, 200, "response code is not 200")

        # created_team = Team.objects.get(name=team_data["name"])
        # self.assertIsNotNone(created_team, "team is not created")


if __name__ == '__main__':
    TestCase.main()
