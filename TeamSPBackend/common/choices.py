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
