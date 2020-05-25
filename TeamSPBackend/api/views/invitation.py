# -*- coding: utf-8 -*-

import ujson

from django.http.response import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.utils.timezone import now
from django.contrib.sessions.models import Session

from TeamSPBackend.common.utils import make_json_response, init_http_response
from TeamSPBackend.common.choices import InvitationStatus
from TeamSPBackend.invitation.models import Invitation


@require_http_methods(['POST', 'GET'])
def invitation_router(request, *args, **kwargs):
    subject_id = None
    for arg in args:
        if isinstance(arg, dict):
            subject_id = arg.get('id', None)
    if request.method == 'POST':
        return add_invitation(request, subject_id)
    elif request.method == 'GET':
        return HttpResponseNotAllowed(['POST'])
    return HttpResponseNotAllowed(['POST'])


def add_invitation(request, subject_id: int):
    param = ujson.loads(request.body)
    invitations = list()
    try:
        timestamp = int(now().timestamp())
        expired = timestamp + 60 * 60 * 24 * 7
        users = param['users']
        for user in users:
            first_name = user['first_name']
            last_name = user['last_name']
            email = user['email']
            user_id = user['id'] if 'id' in user else None
            invitation = Invitation(subject_id=subject_id, supervisor_id=user_id, key='xxx', first_name=first_name,
                                    last_name=last_name, email=email, operator='xxx', create_date=timestamp,
                                    expired=expired, status=InvitationStatus.waiting)
            invitations.append(invitation)

    except Exception as e:
        resp = init_http_response(200, e)
        return make_json_response(HttpResponseBadRequest, resp)

    for invite in invitations:
        invite.save()

    resp = init_http_response(200, 'Success')
    return make_json_response(HttpResponse, resp)
