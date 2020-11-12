from django.test import TestCase, Client
from django.http import HttpRequest


class GetConfluenceContributionsTestCase(TestCase):

    def setUp(self):
        # Set atl credentials
        session = self.client.session
        session["user"] = {
            "atl_username": "yho4",
            "atl_password": "mil1maci"
        }
        session.save()

    def test_get_confluence_contributions(self):
        """
        Tests the function for the API: GET '/confluence/spaces/<space_key>/pages/contributions'
        Note: It is compulsory to be logged into Unimelb's VPN first
        """
        space_key = "SWEN900132020SP"
        url = "/api/v1/confluence/spaces/" + space_key + "/pages/contributions"
        response = self.client.get(url)
        hasAllContributed = True
        for user, count in response.json()["data"].items():
            if count == 0:
                hasAllContributed = False
                break
        self.assertTrue(hasAllContributed, "At least one user has zero contributions")
