from django.test import TestCase, Client
from django.http import HttpRequest
#  import sys
import hashlib
import names

from TeamSPBackend.test.utils import login_helpers, object_creation_helpers
from TeamSPBackend.account.models import User
from TeamSPBackend.api.views.account import get_supervisor
from TeamSPBackend.common.choices import Roles

#  sys.path.append('/Users/keri/git/TeamSPBackend/TeamSPBackend' + '/..')


class GetSupervisorTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        object_creation_helpers.createGenericAdmin()

    def setUp(self):
        # login first
        login_helpers.login(self.client)

        # Create 3 supervisors
        self.supervisors_names = {}
        # Note each supervisors' id offfset by 1 as there is an existing user before any of the supervisors -> admin
        for i in range(3):
            first_name = names.get_first_name()
            last_name = names.get_last_name()
            email = first_name + "@gmail.com"
            userDetails = {'first_name': first_name,
                           'last_name': last_name, 'email': email}
            self.supervisors_names[str(i +
                                       2)] = {'first_name': first_name, 'last_name': last_name, 'full_name': first_name + ' ' + last_name}
            object_creation_helpers.createUser(
                Roles.supervisor, userDetails)

    def test_get_supervisor(self):

        get_supervisor_1_resp = self.client.get('/api/v1/supervisor/2')
        get_supervisor_2_resp = self.client.get('/api/v1/supervisor/3')
        get_supervisor_3_resp = self.client.get('/api/v1/supervisor/4')

        # Assert response codes
        self.assertEqual(get_supervisor_1_resp.status_code,
                         200, "response code is not 200")
        self.assertEqual(get_supervisor_2_resp.status_code,
                         200, "response code is not 200")
        self.assertEqual(get_supervisor_3_resp.status_code,
                         200, "response code is not 200")

        self.assertEqual(
            get_supervisor_1_resp.json()['data']['name'], self.supervisors_names["2"]['full_name'], "supervisor 1 name is not right")
        self.assertEqual(
            get_supervisor_2_resp.json()['data']['name'], self.supervisors_names["3"]['full_name'], "supervisor 2 name is not right")
        self.assertEqual(
            get_supervisor_3_resp.json()['data']['name'], self.supervisors_names["4"]['full_name'], "supervisor 3 name is not right")

    def test_multiget_supervisor(self):
        response = self.client.get('/api/v1/supervisor')

        # Assert response code
        self.assertEqual(response.status_code, 200, "response code is not 200")

        # Assert number of supervisors returned
        self.assertListEqual(
            response.json()['data']['supervisors'], [2, 3, 4], "list of supervisor ids is not correct")


if __name__ == '__main__':
    TestCase.main()
