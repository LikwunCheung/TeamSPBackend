# -*- coding: utf-8 -*-
from enum import Enum


class Choice(object):
    key = None
    msg = None

    def __init__(self, key: int, msg: str):
        self.key = key
        self.msg = msg


class MyEnum(Enum):

    @property
    def key(self):
        return self.value.key

    @property
    def msg(self):
        return self.value.msg


class RespCode(MyEnum):
    success = Choice(0, 'success')
    server_error = Choice(-1, 'server error')
    invalid_parameter = Choice(-2, 'invalid parameter')
    login_fail = Choice(-3, 'login fail')
    not_logged = Choice(-4, 'need login')
    account_existed = Choice(-5, 'existed account')
    invalid_op = Choice(-6, 'invalid operation')
    subject_existed = Choice(-7, 'existed subject')
    permission_deny = Choice(-8, 'permission deny')
    team_existed = Choice(-9, 'existed team')
    incorrect_body = Choice(-10, 'incorrect body')
    confluence_api_error = Choice(-11, "confluence python api error")
    config_not_found = Choice(-12, "confluence config file not found")


class InvitationStatus(MyEnum):
    waiting = Choice(0, 'waiting for invitation')
    sent = Choice(1, 'invitation sent')
    accepted = Choice(2, 'invitation accepted')
    rejected = Choice(3, 'invitation rejected')
    expired = Choice(4, 'invitation expired')


class InvitationRespCode(MyEnum):
    success = Choice(0, 'success')
    invalid_email = Choice(-1, 'invalid email')
    send_fail = Choice(-2, 'send invitation fail')
    existed = Choice(-3, 'invitation existed')


class Status(MyEnum):
    invalid = Choice(0, 'invalid')
    valid = Choice(1, 'valid')


class Roles(MyEnum):
    admin = Choice(0, 'administrator')
    supervisor = Choice(1, 'supervisor')
    coordinator = Choice(2, 'coordinator')


def get_message(choices, index):
    key = list(choices)[index]
    return choices[key].msg


def get_keys(choices):
    if not isinstance(choices, list):
        raise ValueError('incorrect choice')
    return [x.value.key for x in choices]


if __name__ == "__main__":
    pass
