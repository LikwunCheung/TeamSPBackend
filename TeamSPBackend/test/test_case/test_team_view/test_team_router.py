from django.test import TestCase
import sys

from TeamSPBackend.team.models import Team

sys.path.append('/Users/keri/git/TeamSPBackend/TeamSPBackend' + '/..')


class TeamRouterTestCase(TestCase):

    def setUpTestData(self):
        self.test_team = Team()

    # def test_get_team(self):


if __name__ == '__main__':
    TestCase.main()
