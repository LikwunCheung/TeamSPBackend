from TeamSPBackend.common.choices import Roles
from TeamSPBackend.account.models import User
from TeamSPBackend.subject.models import Subject
from TeamSPBackend.test.utils import login_helpers, object_creation_helpers
from django.test import TestCase, Client
from django.http import HttpRequest

import names


class AddSubjectTestCase(TestCase):

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

    def test_add_subject(self):
        """
        Tests the function for the API: Post '/subject'
        """
        coordinatorId = User.objects.get(email=self.client.session["coordinator_1_details"]["email"]).user_id
        subjectData = {"code": "SWEN90013", "name": "geng geng", "coordinator_id": coordinatorId}
        response = self.client.post('/api/v1/subject', data=subjectData, content_type="application/json")

        createdSub = Subject.objects.get(subject_code="SWEN90013")

        self.assertEqual(createdSub.name, "geng geng", "subject not created or subject name is not equal")
