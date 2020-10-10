from TeamSPBackend.common.choices import Roles
from TeamSPBackend.test.utils import login_helpers, object_creation_helpers
from TeamSPBackend.account.models import User
from django.test import TestCase, Client
from django.http import HttpRequest
import hashlib
import names


#  sys.path.append('/Users/keri/git/TeamSPBackend/TeamSPBackend' + '/..')


class GetSubjectTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        object_creation_helpers.createGenericAdmin()

    def setUp(self):
        # login first
        login_helpers.login(self.client)

        # Create 2 coordinators
        first_name = names.get_first_name()
        last_name = names.get_last_name()
        coordinator_1_details = {
            "first_name": first_name, "last_name": last_name, "email": first_name + last_name + "@gmail.com"
        }
        object_creation_helpers.createUser(
            Roles.coordinator, coordinator_1_details)
        first_name = names.get_first_name()
        last_name = names.get_last_name()
        coordinator_2_details = {
            "first_name": first_name, "last_name": last_name, "email": first_name + last_name + "@gmail.com"
        }
        object_creation_helpers.createUser(
            Roles.coordinator, coordinator_2_details)

        # Create subjects and assign each coordinator to one of the two subjects
        coordinator_1_id = User.objects.get(
            email=coordinator_1_details["email"]).user_id
        coordinator_2_id = User.objects.get(
            email=coordinator_2_details["email"]).user_id
        object_creation_helpers.createSubject(
            "SWEN90013", "Master Advanced Software Project", coordinator_1_id)
        object_creation_helpers.createSubject(
            "SWEN90014", "Master Software Engineering Project", coordinator_2_id)

    def test_get_subject(self):
        """
        Tests the function for the API: Get '/subject/<int:id>'
        """
        response = self.client.get('/api/v1/subject/1')
        data = response.json()["data"]
        subject_details = (data["code"], data["name"])
        self.assertEqual(subject_details, ("SWEN90013", "Master Advanced Software Project"),
                         "Subject id 1 details are not correct")

    def test_multiget_subject(self):
        """
        Tests the function for the API: Get '/subject'
        """
        response = self.client.get('/api/v1/subject')
        self.assertEquals(response.json()["data"]["ids"], [
            1, 2], "returned subject ids are not correct")


if __name__ == '__main__':
    TestCase.main()
