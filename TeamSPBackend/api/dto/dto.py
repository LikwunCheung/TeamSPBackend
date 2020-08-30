# -*- coding: utf-8 -*-
import hashlib

from TeamSPBackend.common.config import SALT
from TeamSPBackend.common.utils import email_validate


class LoginDTO(object):

    def __init__(self):
        self.username = None
        self.email = None
        self.password = None
        self.md5 = None

    def encrypt(self):
        self.password = self.password + SALT
        self.md5 = hashlib.sha3_256(self.password.encode()).hexdigest()

    def validate(self):
        return not (not self.username and not self.email)


class AddAccountDTO(object):

    def __init__(self):
        self.username = None
        self.email = None
        self.password = None
        self.role = None
        self.first_name = None
        self.last_name = None
        self.md5 = None

    def encrypt(self):
        self.password = self.password + SALT
        self.md5 = hashlib.sha3_256(self.password.encode()).hexdigest()

    def not_empty(self):
        return not (not self.username or not self.email or not self.password or self.role is None or not self.first_name
                    or not self.last_name)

    def validate(self):
        return 0 <= self.role <= 2


class UpdateAccountDTO(object):

    def __init__(self):
        self.old_password = None
        self.password = None
        self.role = None
        self.first_name = None
        self.last_name = None
        self.old_md5 = None
        self.md5 = None

    def encrypt(self):
        if not self.old_password or not self.password:
            return

        self.old_password = self.old_password + SALT
        self.password = self.password + SALT
        self.old_md5 = hashlib.sha3_256(self.old_password.encode()).hexdigest()
        self.md5 = hashlib.sha3_256(self.password.encode()).hexdigest()

    def validate(self):
        if self.role:
            return 0 <= self.role <= 2
        return True


class AddSubjectDTO(object):

    def __init__(self):
        self.code = None
        self.name = None
        self.coordinator_id = 0

    def not_empty(self):
        return not (not self.code or not self.name or self.coordinator_id is 0)


class InviteUserDTO(object):

    def __init__(self):
        self.first_name = None
        self.last_name = None
        self.email = None

    def not_empty(self):
        return not (not self.first_name or not self.last_name or not self.email)

    def validate(self):
        return email_validate(self.email)
