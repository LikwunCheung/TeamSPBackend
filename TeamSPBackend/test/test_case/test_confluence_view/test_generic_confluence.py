from django.test import TestCase, Client
from TeamSPBackend.common.choices import RespCode


class GenericeConfluenceTestCase(TestCase):

    def setUp(self):
        session = self.client.session
        session["user"] = {
            "atl_username": "yho4",
            "atl_password": "mil1maci"
        }
        session.save()

    def test_get_all_groups_success(self):
        """
        Tests the success scenario for function get_all_groups
        """
        response = self.client.get('/api/v1/confluence/groups')
        self.assertEqual(response.json()["code"], RespCode.success.value.key, "response is not success")

    def test_get_all_groups_failure(self):
        """
        Tests the failure scenario for function get_all_groups
        """
        session = self.client.session
        session["user"] = {
            "atl_username": "yho4",
            "atl_password": "wrongpw"
        }
        session.save()
        response = self.client.get('/api/v1/confluence/groups')
        self.assertEqual(response.json()["code"], -1, "response code is not -1")

    def test_get_space_success(self):
        """
        Tests the success scenario for function get_space
        """
        space_key = "SWEN900132020SP"
        response = self.client.get('/api/v1/confluence/spaces/' + space_key)
        self.assertEqual(response.json()["code"], RespCode.success.value.key, "response is not success")

    def test_get_space_failure(self):
        """
        Tests the failure scenario for function get_space
        """
        space_key = "SWEN900132020SP"
        session = self.client.session
        session["user"] = {
            "atl_username": "yho4",
            "atl_password": "wrongpw"
        }
        session.save()
        response = self.client.get('/api/v1/confluence/spaces/' + space_key)
        self.assertEqual(response.json()["code"], -1, "response code is not -1")

    def test_get_pages_of_space_success(self):
        """
        Tests the success scenario for function get_pages_of_space
        """
        space_key = "SWEN900132020SP"
        response = self.client.get('/api/v1/confluence/spaces/' + space_key + '/pages')
        self.assertEqual(response.json()["code"], RespCode.success.value.key, "response is not success")

    def test_get_space_failure(self):
        """
        Tests the failure scenario for function get_pages_of_space
        """
        space_key = "SWEN900132020SP"
        session = self.client.session
        session["user"] = {
            "atl_username": "yho4",
            "atl_password": "wrongpw"
        }
        session.save()
        response = self.client.get('/api/v1/confluence/spaces/' + space_key + '/pages')
        self.assertEqual(response.json()["code"], -1, "response code is not -1")

    def test_search_team_success(self):
        """
        Tests the success scenario for function search_team
        """
        keyword = "sp"
        response = self.client.get('/api/v1/confluence/groups/searchteam/' + keyword)
        self.assertEqual(response.json()["code"], RespCode.success.value.key, "response is not success")

    def test_search_team_failure(self):
        """
        Tests the failure scenario for function search_team
        """
        keyword = "sp"
        session = self.client.session
        session["user"] = {
            "atl_username": "yho4",
            "atl_password": "wrongpw"
        }
        session.save()
        response = self.client.get('/api/v1/confluence/groups/searchteam/' + keyword)
        self.assertEqual(response.json()["code"], -1, "response code is not -1")

    def test_get_group_members_success(self):
        """
        Tests the success scenario for function search_team
        """
        group = "swen90013-2020-sp"
        response = self.client.get('/api/v1/confluence/groups/' + group + '/members')
        self.assertEqual(response.json()["code"], RespCode.success.value.key, "response is not success")

    def test_get_group_members_failure(self):
        """
        Tests the failure scenario for function search_team
        """
        group = "swen90013-2020-sp"
        session = self.client.session
        session["user"] = {
            "atl_username": "yho4",
            "atl_password": "wrongpw"
        }
        session.save()
        response = self.client.get('/api/v1/confluence/groups/' + group + '/members')
        self.assertEqual(response.json()["code"], -1, "response code is not -1")

    def test_get_user_details_success(self):
        """
        Tests the success scenario for function get_user_details
        """
        member = 'yho4'
        response = self.client.get('/api/v1/confluence/users/' + member)
        self.assertEqual(response.json()["code"], RespCode.success.value.key, "response is not success")

    def test_get_user_details_failure(self):
        """
        Tests the failure scenario for function get_user_details
        """
        member = 'arandomusername'
        response = self.client.get('/api/v1/confluence/users/' + member)
        self.assertEqual(response.json()["code"], -1, "response code is not -1")

    def test_get_subject_supervisors_success(self):
        """
        Tests the success scenario for function get_subject_supervisors
        """
        subject_code = "swen90013"
        year = "2020"
        response = self.client.get('/api/v1/subject/' + subject_code + '/' + year + '/supervisors')
        self.assertEqual(response.json()["code"], RespCode.success.value.key, "response is not success")

    def test_get_subject_supervisors_failure(self):
        """
        Tests the failure scenario for function get_subject_supervisors
        """
        subject_code = "swen90013"
        year = "2020"
        session = self.client.session
        session["user"] = {
            "atl_username": "yho4",
            "atl_password": "wrongpw"
        }
        session.save()
        response = self.client.get('/api/v1/subject/' + subject_code + '/' + year + '/supervisors')
        self.assertEqual(response.json()["code"], -1, "response code is not -1")

    def test_get_page_contributors_success(self):
        """
        Tests the success scenario for function get_page_contributors
        """
        page_id = "56855170"
        space_key = "SWEN900132020SP"
        response = self.client.get('/api/v1/confluence/spaces/' + space_key + '/pages/' + page_id)
        self.assertEqual(response.json()["code"], RespCode.success.value.key, "response is not success")

    def test_get_page_contributors_failure(self):
        """
        Tests the success scenario for function get_page_contributors
        """
        page_id = "56855170"
        session = self.client.session
        session["user"] = {
            "atl_username": "yho4",
            "atl_password": "wrongpw"
        }
        session.save()
        space_key = "SWEN900132020SP"
        response = self.client.get('/api/v1/confluence/spaces/' + space_key + '/pages/' + page_id)
        self.assertEqual(response.json()["code"], -1, "response code is not -1")
