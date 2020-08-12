# -*- coding: utf-8 -*-

import ujson
import random
import string

from django.http.response import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.utils.timezone import now
from django.contrib.sessions.models import Session

from TeamSPBackend.common.utils import make_json_response, init_http_response, check_user_login
from TeamSPBackend.common.choices import InvitationStatus, RespCode
from TeamSPBackend.common.config import SINGLE_PAGE_LIMIT
from TeamSPBackend.invitation.models import Invitation


@require_http_methods(['POST', 'GET'])
@check_user_login
def invitation_router(request, *args, **kwargs):
    subject_id = None
    for arg in args:
        if isinstance(arg, dict):
            subject_id = arg.get('id', None)
    if request.method == 'POST':
        return add_invitation(request, subject_id)
    elif request.method == 'GET':
        return get_invitation(request, subject_id)
    return HttpResponseNotAllowed(['POST'])


def add_invitation(request, subject_id: int):
    """
    TODO: check email in account
    TODO: send email

    :param request:
    :param subject_id:
    :return:
    """
    param = ujson.loads(request.body)
    invitations = list()

    user = request.session.get('user')
    user_id = user['id']

    timestamp = int(now().timestamp())

    expired = timestamp + 60 * 60 * 24 * 7
    invite_users = param['users']
    failed = list()

    for invite_user in invite_users:
        first_name = invite_user['first_name']
        last_name = invite_user['last_name']
        email = invite_user['email']

        if Invitation.objects.filter(subject_id=subject_id, email=email,
                                     status__lte=InvitationStatus.accepted.value.key).exists():
            failed.append(dict(
                email=email,
                first_name=first_name,
                last_name=last_name,
            ))

        key = ''.join([''.join(random.sample(string.ascii_letters + string.digits, 8)) for i in range(8)])
        invite_user_id = invite_user['id'] if 'id' in invite_user else None
        invitation = Invitation(subject_id=subject_id, supervisor_id=invite_user_id, key=key, first_name=first_name,
                                last_name=last_name, email=email, operator=user_id, create_date=timestamp,
                                expired=expired, status=InvitationStatus.waiting.value.key)
        invitations.append(invitation)

    for invite in invitations:
        invite.save()

    data = dict(
        failed=failed
    )
    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    resp['data'] = data
    return make_json_response(HttpResponse, resp)


def get_invitation(request, subject_id: int):
    """
    TODO: update expired status

    :param request:
    :param subject_id:
    :return:
    """

    finished = request.GET.get('finished', None)
    offset = int(request.POST.get('offset', 0))
    has_more = 0

    kwargs = dict(
        subject_id=subject_id,
    )
    if finished is not None:
        if int(finished) == 0:
            kwargs['status__lt'] = InvitationStatus.accepted.value.key
        else:
            kwargs['status__gte'] = InvitationStatus.accepted.value.key

    invitations = Invitation.objects.filter(**kwargs).order_by('invitation_id')[offset: offset + SINGLE_PAGE_LIMIT + 1]
    if len(invitations) > SINGLE_PAGE_LIMIT:
        invitations = invitations[: SINGLE_PAGE_LIMIT]
        has_more = 1
    offset += len(invitations)

    if len(invitations) == 0:
        data = dict(
            invitations=[],
            has_more=has_more,
            offset=offset,
        )
        resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return make_json_response(HttpResponse, resp)

    data = dict(
        invitation=[
            dict(
                id=invitation.invitation_id,
                name=invitation.get_name(),
                email=invitation.email,
                expired=invitation.expired,
                status=invitation.status
            ) for invitation in invitations
        ],
        offset=offset,
        has_more=has_more
    )

    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    resp['data'] = data
    return make_json_response(HttpResponse, resp)
