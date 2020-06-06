# -*- coding: utf-8 -*-
from enum import Enum, unique


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

class AccountStatus(Enum):
    invalid = 0
    valid = 1

    AccountStatusChoice = (
        (invalid, 'account is invalid'),
        (valid, 'account is valid'),
    )

class Roles(Enum):
    supervisor = 1
    coordinator = 2

    RolesChoice = (
        (supervisor, 'supervisor'),
        (coordinator, 'coordinator'),
    )

class TeamStatus(Enum):
    expired = 0
    unexpired = 1

    TeamStatusChoice = (
        (expired, 'team is expired'),
        (unexpired, 'team is unexpired'),
    )