# -*- coding: utf-8 -*-

import hashlib
import base64
import re

from Crypto.Cipher import AES

from TeamSPBackend.common.config import SALT
from TeamSPBackend.common.utils import email_validate, auto_fill


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
        if not isinstance(self.role, int):
            return False
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
        self.atl_username = None
        self.atl_password = None
        self.aes = None

    def encrypt(self):
        if not self.old_password or not self.password:
            return

        self.old_password = self.old_password + SALT
        self.password = self.password + SALT
        self.old_md5 = hashlib.sha3_256(self.old_password.encode()).hexdigest()
        self.md5 = hashlib.sha3_256(self.password.encode()).hexdigest()

    def encrypt_aes(self):
        if self.atl_password is None:
            return
        aes = AES.new(auto_fill(SALT), AES.MODE_ECB)
        self.aes = base64.encodebytes(aes.encrypt(auto_fill(self.atl_password)))

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


class InviteAcceptDTO(object):

    def __init__(self):
        self.key = None
        self.username = None
        self.password = None
        self.first_name = None
        self.last_name = None
        self.md5 = None

    def not_empty(self):
        return not (not self.key or not self.username or not self.password or not self.first_name or not self.last_name)

    def encrypt(self):
        self.password = self.password + SALT
        self.md5 = hashlib.sha3_256(self.password.encode()).hexdigest()


class AddTeamDTO(object):

    def __init__(self):
        self.team = None
        self.subject = None
        self.year = None
        self.project = None

    def not_empty(self):
        return not (not self.team or not self.subject or not self.year or not self.project)


class UpdateTeamDTO(object):

    def __init__(self):
        self.supervisor_id = None
        self.secondary_supervisor_id = None


class TeamMemberDTO(object):

    def __init__(self):
        self.git_name = None
        self.slack_email = None
        self.atl_account = None


class TeamConfigurationDTO(object):

    def __init__(self):
        self.slack_workspace = None
        self.confluence_workspace = None
        self.jira_workspace = None
        self.git_repository = None


class GitDTO(object):

    def __init__(self):
        self.url = None
        self.branch = None
        self.author = None
        self.after = None
        self.before = None

    @property
    def valid_url(self):
        return self.url and re.match(r'^https://github.com(/\w+)+', self.url)

    @property
    def second_before(self):
        if not self.before:
            return None
        return self.before // 1000

    @property
    def second_after(self):
        if not self.after:
            return None
        return self.after // 1000
