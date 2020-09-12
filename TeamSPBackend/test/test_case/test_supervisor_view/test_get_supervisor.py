from django.test import TestCase, Client
from django.http import HttpRequest
import sys
import hashlib
import names

from TeamSPBackend.test.utils import login_helpers
from TeamSPBackend.account.models import User
from TeamSPBackend.api.views.account import get_supervisor

sys.path.append('/Users/keri/git/TeamSPBackend/TeamSPBackend' + '/..')


class GetSupervisorTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        login_helpers.createAdmin()

    def test_get_supervisor(self):
        # login first
        username = "admin"
        password = "admin"
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

        # List of supervisor ids, first names, and last names to verify
        supervisors_names = {}
        # Create 5 supervisors
        for i in range(5):
            first_name = names.get_first_name()
            last_name = names.get_last_name()
            supervisors_names[str(i +
                                  1)] = {'first_name': first_name, 'last_name': last_name, 'full_name': first_name + ' ' + last_name}
            login_helpers.createSupervisor(first_name, last_name)

        get_supervisor_1_resp = self.client.get('api/v1/supervisor/1')
        get_supervisor_2_resp = self.client.get('api/v1/supervisor/2')
        get_supervisor_3_resp = self.client.get('api/v1/supervisor/3')
        get_supervisor_4_resp = self.client.get('api/v1/supervisor/4')
        get_supervisor_5_resp = self.client.get('api/v1/supervisor/5')

        # Assert response codes
        self.assertEqual(get_supervisor_1_resp.status_code,
                         200, "response code is not 200")
        self.assertEqual(get_supervisor_2_resp.status_code,
                         200, "response code is not 200")
        self.assertEqual(get_supervisor_3_resp.status_code,
                         200, "response code is not 200")
        self.assertEqual(get_supervisor_4_resp.status_code,
                         200, "response code is not 200")
        self.assertEqual(get_supervisor_5_resp.status_code,
                         200, "response code is not 200")

        # Assert each supervisor name
        supervisor_1_full_name = get_supervisor_1_resp.json().first_name + ' ' + \
            get_supervisor_1_resp.json().last_name
        supervisor_2_full_name = get_supervisor_2_resp.json().first_name + ' ' + \
            get_supervisor_2_resp.json().last_name
        supervisor_3_full_name = get_supervisor_3_resp.json().first_name + ' ' + \
            get_supervisor_3_resp.json().last_name
        supervisor_4_full_name = get_supervisor_4_resp.json().first_name + ' ' + \
            get_supervisor_4_resp.json().last_name
        supervisor_5_full_name = get_supervisor_5_resp.json().first_name + ' ' + \
            get_supervisor_5_resp.json().last_name
        self.assertEqual(
            supervisor_1_full_name, supervisors_names["1"].full_name, "supervisor 1 name is not right")
        self.assertEqual(
            supervisor_2_full_name, supervisors_names["2"].full_name, "supervisor 2 name is not right")
        self.assertEqual(
            supervisor_3_full_name, supervisors_names["3"].full_name, "supervisor 3 name is not right")
        self.assertEqual(
            supervisor_4_full_name, supervisors_names["4"].full_name, "supervisor 4 name is not right")
        self.assertEqual(
            supervisor_5_full_name, supervisors_names["5"].full_name, "supervisor 5 name is not right")


if __name__ == '__main__':
    TestCase.main()
