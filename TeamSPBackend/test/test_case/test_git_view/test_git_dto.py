import unittest

from TeamSPBackend.api.dto.dto import GitDTO, LoginDTO


class MyTestCase(unittest.TestCase):

    def test_valid_url(self):
        g = GitDTO()
        g.url = "https://github.com/LikwunCheung/TeamSPBackend.git"
        self.assertEqual(g.valid_url.group(), "https://github.com/LikwunCheung/TeamSPBackend")

    def test_invalid_url(self):
        g = GitDTO()
        g.url = "https://false.com/LikwunCheung/TeamSPBackend.git"
        self.assertEqual(g.valid_url, None)

    def test_second_before(self):
        g = GitDTO()
        g.url = "https://github.com/LikwunCheung/TeamSPBackend.git"
        g.before = 1511141532000
        self.assertEqual(g.second_before, 1511141532)

    def test_second_after(self):
        g = GitDTO()
        g.url = "https://github.com/LikwunCheung/TeamSPBackend.git"
        self.assertEqual(g.second_after, None)


if __name__ == '__main__':
    unittest.main()
