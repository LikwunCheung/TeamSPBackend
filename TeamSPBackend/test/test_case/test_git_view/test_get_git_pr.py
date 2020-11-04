import unittest

from TeamSPBackend.test.utils import object_creation_helpers, login_helpers
from django.test import TestCase


class GetGitPR(TestCase):
    @classmethod
    def setUpTestData(cls):
        object_creation_helpers.createGenericAdmin()

    def setUp(self):
        # login first
        login_helpers.login(self.client)

    def test_get_total_pr(self):
        """
                Test the function for the API: POST /api/v1/git/pullrequest
                Search for total contribution
                """
        url = "/api/v1/git/pullrequest"
        data = {
            "url": "https://github.com/LikwunCheung/TeamSPBackend",
            # "author": "Procyon"
        }
        # get_git_commits(data=data)
        response = self.client.post(url, data=data, content_type="application/json")
        self.assertNotEqual(response.json()["data"], None)
        # self.assertEqual(response.status_code, 200, "response code is not 200")

        # d = get_git_commits(request = data)
        # self.assertEqual(d.status_code, 200)

    def test_get_individual_pr(self):
        """
        Test the function for the API: POST /api/v1/git/pullrequest
        Search for individual contribution
        """

        url = "/api/v1/git/pullrequest"
        data = {
            "url": "https://github.com/LikwunCheung/TeamSPBackend",
            "author": "Procyon1996"
        }
        tag_1 = 0
        tag_2 = 1
        response = self.client.post(url, data=data, content_type="application/json")
        for commit in response.json()["data"]['commits']:
            if commit['author'] != 'Procyon1996':
                tag_1 = 1
            if commit['author'] == 'Procyon1996':
                tag_2 = 0
        self.assertEqual(tag_1 & tag_2, 0)
    def test_git_date(self):
        url = "/api/v1/git/pr"
        data = {
            "url": "https://github.com/LikwunCheung/TeamSPBackend",
            "after": 1500000000000,
            "before": 1600000000000
        }
        response = self.client.post(url, data=data, content_type="application/json")
        flag = True
        for commit in response.json()["data"]['commits']:
            if commit['date'] < 1500000000000:
                flag = False
            elif commit['date'] > 1600000000000:
                flag = False
        self.assertEqual(flag, True)


if __name__ == '__main__':
    unittest.main()
