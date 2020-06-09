# -*- coding: utf-8 -*-
from enum import Enum, unique


@unique
class RespCode(Enum):
    success = 0
    server_error = -1
    invalid_parameter = -2
    login_fail = -3
    not_logged = -4
    account_existed = -5
    invalid_op = -6

    RespCodeChoice = (
        (success, 'success'),
        (server_error, 'server error'),
        (invalid_parameter, 'invalid parameter'),
        (login_fail, 'login fail'),
        (not_logged, 'need login'),
        (account_existed, 'existed account'),
        (invalid_op, 'invalid operation'),
    )


@unique
class InvitationStatus(Enum):
    waiting = 0
    sent = 1
    accepted = 2
    rejected = 3
    expired = 4

    InvitationStatusChoice = (
        (waiting, 'waiting for invitation'),
        (sent, 'invitation sent'),
        (accepted, 'invitation accepted'),
        (rejected, 'invitation rejected'),
        (expired, 'invitation expired')
    )


@unique
class Status(Enum):
    invalid = 0
    valid = 1

    StatusChoice = (
        (invalid, 'invalid'),
        (valid, 'valid'),
    )


class Roles(Enum):
    admin = 0
    supervisor = 1
    coordinator = 2

    RolesChoice = (
        (admin, 'administrator'),
        (supervisor, 'supervisor'),
        (coordinator, 'coordinator'),
    )
