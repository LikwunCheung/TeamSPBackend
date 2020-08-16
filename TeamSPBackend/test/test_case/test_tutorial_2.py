import sys

sys.path.append('/Users/keri/git/TeamSPBackend/TeamSPBackend' + '/..')

import unittest

from TeamSPBackend.api.dto.dto import LoginDTO


class MyTestCase(unittest.TestCase):

    def test_login_initial(self):
        d = LoginDTO()
        self.assertEqual(d.password, None)

    def test_login_encrypt(self):
        d = LoginDTO()
        d.password = "12345"
        pwd = d.password
        d.encrypt()
        self.assertNotEqual(d.password, pwd)


if __name__ == '__main__':
    unittest.main()
