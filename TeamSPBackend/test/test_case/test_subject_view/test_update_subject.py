from TeamSPBackend.common.choices import Roles
from TeamSPBackend.account.models import User
from TeamSPBackend.subject.models import Subject
from TeamSPBackend.test.utils import login_helpers, object_creation_helpers
from django.test import TestCase, Client
from django.http import HttpRequest

import names


class UpdateSubjectTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        object_creation_helpers.createGenericAdmin()

    def setUp(self):
        login_helpers.login(self.client)
        # Create a coordinator
        first_name = names.get_first_name()
        last_name = names.get_last_name()
        session = self.client.session
        session["coordinator_1_details"] = {
            "first_name": first_name, "last_name": last_name, "email": first_name + last_name + "@gmail.com"
        }
        session.save()
        object_creation_helpers.createUser(Roles.coordinator, session["coordinator_1_details"])
        coordinator_1_id = User.objects.get(
            email=session["coordinator_1_details"]["email"]).user_id
        object_creation_helpers.createSubject(
            "SWEN90013", "Master Advanced Software Project", coordinator_1_id)

    def test_update_subject_success(self):
        """
        Tests the function for the API: Post '/subject/<int:id>/update'
        """
        subjectData = {
            "name": "newName"
        }
        response = self.client.post('/api/v1/subject/1/update', data=subjectData, content_type="application/json")
        print("response is " + str(response.json()))

        updatedSub = Subject.objects.get(subject_id=1)
        self.assertEqual(updatedSub.name, "newName", "subject name is not updated")
