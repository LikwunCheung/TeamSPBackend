from django.test import TestCase, Client

from TeamSPBackend.common.choices import Roles
from TeamSPBackend.team.models import Team, TeamMember, Student
from TeamSPBackend.account.models import User, Account
from TeamSPBackend.api.views import team
from TeamSPBackend.test.utils import login_helpers, object_creation_helpers

import names


class MultiGetTeamTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        # set up an admin
        object_creation_helpers.createGenericAdmin()

        # set up a coordinator
        object_creation_helpers.createUser(Roles.coordinator, object_creation_helpers.generateUserDetails())

        # set up a supervisor
        object_creation_helpers.createUser(Roles.supervisor, object_creation_helpers.generateUserDetails())

        # set up a second primary supervisor
        object_creation_helpers.createUser(Roles.supervisor, object_creation_helpers.generateUserDetails())

        # set up a secondary supervisor
        object_creation_helpers.createUser(Roles.supervisor, object_creation_helpers.generateUserDetails())

        # set up a subject
        object_creation_helpers.createSubject('123', 'test_subject', 2)

        # set up three teams
        team_data = {
            "name": "team_1",
            "subject_code": '123',
            "supervisor_id": 3,
            "secondary_supervisor_id": 5,
            "year": "2020",
            "create_date": "01012020",
            "project_name": "test_project_1",
            "sprint_start_0": "1",
            "sprint_end_0": "1",
            "sprint_start_1": "1",
            "sprint_end_1": "1",
            "sprint_start_2": "1",
            "sprint_end_2": "1",
            "sprint_start_3": "1",
            "sprint_end_3": "1",
            "sprint_start_4": "1",
            "sprint_end_4": "1",
        }
        team = Team(name=team_data["name"],
                    subject_code=team_data["subject_code"],
                    supervisor_id=team_data["supervisor_id"],
                    secondary_supervisor_id=team_data["secondary_supervisor_id"],
                    year=team_data["year"],
                    create_date=team_data["create_date"],
                    project_name=team_data["project_name"],
                    sprint_start_0=team_data["sprint_start_0"],
                    sprint_end_0=team_data["sprint_end_0"],
                    sprint_start_1=team_data["sprint_start_1"],
                    sprint_end_1=team_data["sprint_end_1"],
                    sprint_start_2=team_data["sprint_start_2"],
                    sprint_end_2=team_data["sprint_end_2"],
                    sprint_start_3=team_data["sprint_start_3"],
                    sprint_end_3=team_data["sprint_end_3"],
                    sprint_start_4=team_data["sprint_start_4"],
                    sprint_end_4=team_data["sprint_end_4"],
                    )
        team.save()
        team_data = {
            "name": "team_2",
            "subject_code": '123',
            "supervisor_id": 3,
            "secondary_supervisor_id": 5,
            "year": "2020",
            "create_date": "01012020",
            "project_name": "test_project_2",
            "sprint_start_0": "1",
            "sprint_end_0": "1",
            "sprint_start_1": "1",
            "sprint_end_1": "1",
            "sprint_start_2": "1",
            "sprint_end_2": "1",
            "sprint_start_3": "1",
            "sprint_end_3": "1",
            "sprint_start_4": "1",
            "sprint_end_4": "1",
        }
        team = Team(name=team_data["name"],
                    subject_code=team_data["subject_code"],
                    supervisor_id=team_data["supervisor_id"],
                    secondary_supervisor_id=team_data["secondary_supervisor_id"],
                    year=team_data["year"],
                    create_date=team_data["create_date"],
                    project_name=team_data["project_name"],
                    sprint_start_0=team_data["sprint_start_0"],
                    sprint_end_0=team_data["sprint_end_0"],
                    sprint_start_1=team_data["sprint_start_1"],
                    sprint_end_1=team_data["sprint_end_1"],
                    sprint_start_2=team_data["sprint_start_2"],
                    sprint_end_2=team_data["sprint_end_2"],
                    sprint_start_3=team_data["sprint_start_3"],
                    sprint_end_3=team_data["sprint_end_3"],
                    sprint_start_4=team_data["sprint_start_4"],
                    sprint_end_4=team_data["sprint_end_4"],
                    )
        team.save()
        team_data = {
            "name": "team_3",
            "subject_code": '123',
            "supervisor_id": 4,
            "secondary_supervisor_id": 5,
            "year": "2020",
            "create_date": "01012020",
            "project_name": "test_project_3",
            "sprint_start_0": "1",
            "sprint_end_0": "1",
            "sprint_start_1": "1",
            "sprint_end_1": "1",
            "sprint_start_2": "1",
            "sprint_end_2": "1",
            "sprint_start_3": "1",
            "sprint_end_3": "1",
            "sprint_start_4": "1",
            "sprint_end_4": "1",
        }
        team = Team(name=team_data["name"],
                    subject_code=team_data["subject_code"],
                    supervisor_id=team_data["supervisor_id"],
                    secondary_supervisor_id=team_data["secondary_supervisor_id"],
                    year=team_data["year"],
                    create_date=team_data["create_date"],
                    project_name=team_data["project_name"],
                    sprint_start_0=team_data["sprint_start_0"],
                    sprint_end_0=team_data["sprint_end_0"],
                    sprint_start_1=team_data["sprint_start_1"],
                    sprint_end_1=team_data["sprint_end_1"],
                    sprint_start_2=team_data["sprint_start_2"],
                    sprint_end_2=team_data["sprint_end_2"],
                    sprint_start_3=team_data["sprint_start_3"],
                    sprint_end_3=team_data["sprint_end_3"],
                    sprint_start_4=team_data["sprint_start_4"],
                    sprint_end_4=team_data["sprint_end_4"],
                    )
        team.save()

    def test_multi_get_team_as_coordinator_success(self):
        """
        Tests the success scenario for function multi_get_team() as a coordinator
        for the API: Get 'team'
        """
        # login as coordinator
        coordinator_acc = Account.objects.get(account_id=2)
        login_helpers.login_with_credentials(self.client, coordinator_acc.username, coordinator_acc.password)
        supervisor_1 = User.objects.get(user_id=3)
        supervisor_2 = User.objects.get(user_id=4)
        secondary_supervisor = User.objects.get(user_id=5)
        expected_teams_data = [
            {
                "id": 1,
                "name": "team_1",
                "project_name": "test_project_1",
                "year": 2020,
                "supervisor": {
                    "id": 3,
                    "name": supervisor_1.get_name(),
                    "email": supervisor_1.email
                },
                "secondary_supervisor": {
                    "id": 5,
                    "name": secondary_supervisor.get_name(),
                    "email": secondary_supervisor.email
                },
            },
            {
                "id": 2,
                "name": "team_2",
                "project_name": "test_project_2",
                "year": 2020,
                "supervisor": {
                    "id": 3,
                    "name": supervisor_1.get_name(),
                    "email": supervisor_1.email
                },
                "secondary_supervisor": {
                    "id": 5,
                    "name": secondary_supervisor.get_name(),
                    "email": secondary_supervisor.email
                },
            },
            {
                "id": 3,
                "name": "team_3",
                "project_name": "test_project_3",
                "year": 2020,
                "supervisor": {
                    "id": 4,
                    "name": supervisor_2.get_name(),
                    "email": supervisor_2.email
                },
                "secondary_supervisor": {
                    "id": 5,
                    "name": secondary_supervisor.get_name(),
                    "email": secondary_supervisor.email
                },
            },
        ]

        response = self.client.get('/api/v1/team')
        self.assertEqual(expected_teams_data, response.json()["data"]["teams"], "multi_get_teams for coordinator is busted")

    def test_multi_get_team_as_supervisor_success(self):
        """
        Tests the success scenario for function multi_get_team() as a supervisor
        for the API: Get 'team'
        """
        # login as supervisor 1
        supervisor_acc = Account.objects.get(account_id=3)
        login_helpers.login_with_credentials(self.client, supervisor_acc.username, supervisor_acc.password)
        supervisor = User.objects.get(user_id=3)
        secondary_supervisor = User.objects.get(user_id=5)
        expected_teams_data = [
            {
                "id": 1,
                "name": "team_1",
                "project_name": "test_project_1",
                "year": 2020,
                "supervisor": {
                    "id": 3,
                    "name": supervisor.get_name(),
                    "email": supervisor.email
                },
                "secondary_supervisor": {
                    "id": 5,
                    "name": secondary_supervisor.get_name(),
                    "email": secondary_supervisor.email
                },
            },
            {
                "id": 2,
                "name": "team_2",
                "project_name": "test_project_2",
                "year": 2020,
                "supervisor": {
                    "id": 3,
                    "name": supervisor.get_name(),
                    "email": supervisor.email
                },
                "secondary_supervisor": {
                    "id": 5,
                    "name": secondary_supervisor.get_name(),
                    "email": secondary_supervisor.email
                },
            },
        ]

        response = self.client.get('/api/v1/team')
        self.assertEqual(expected_teams_data, response.json()["data"]["teams"], "multi_get_teams for coordinator is busted")

    def test_multi_get_team_as_admin_success(self):
        """
        Tests the success scenario for function multi_get_team() as an admin
        for the API: Get 'team'
        """
        # login as the admin
        admin_acc = Account.objects.get(account_id=2)
        login_helpers.login_with_credentials(self.client, admin_acc.username, admin_acc.password)
        supervisor_1 = User.objects.get(user_id=3)
        supervisor_2 = User.objects.get(user_id=4)
        secondary_supervisor = User.objects.get(user_id=5)
        expected_teams_data = [
            {
                "id": 1,
                "name": "team_1",
                "project_name": "test_project_1",
                "year": 2020,
                "supervisor": {
                    "id": 3,
                    "name": supervisor_1.get_name(),
                    "email": supervisor_1.email
                },
                "secondary_supervisor": {
                    "id": 5,
                    "name": secondary_supervisor.get_name(),
                    "email": secondary_supervisor.email
                },
            },
            {
                "id": 2,
                "name": "team_2",
                "project_name": "test_project_2",
                "year": 2020,
                "supervisor": {
                    "id": 3,
                    "name": supervisor_1.get_name(),
                    "email": supervisor_1.email
                },
                "secondary_supervisor": {
                    "id": 5,
                    "name": secondary_supervisor.get_name(),
                    "email": secondary_supervisor.email
                },
            },
            {
                "id": 3,
                "name": "team_3",
                "project_name": "test_project_3",
                "year": 2020,
                "supervisor": {
                    "id": 4,
                    "name": supervisor_2.get_name(),
                    "email": supervisor_2.email
                },
                "secondary_supervisor": {
                    "id": 5,
                    "name": secondary_supervisor.get_name(),
                    "email": secondary_supervisor.email
                },
            },
        ]

        response = self.client.get('/api/v1/team')
        self.assertEqual(expected_teams_data, response.json()["data"]["teams"], "multi_get_teams for admin is busted")
