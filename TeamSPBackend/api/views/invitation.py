# -*- coding: utf-8 -*-

import random
import string

from django.http.response import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.utils.timezone import now
from django.db import transaction

from TeamSPBackend.common.utils import make_json_response, init_http_response, check_user_login, check_body, body_extract
from TeamSPBackend.common.choices import InvitationStatus, RespCode, InvitationRespCode, Status, get_message
from TeamSPBackend.common.config import SINGLE_PAGE_LIMIT
from TeamSPBackend.invitation.models import Invitation
from TeamSPBackend.api.dto.dto import InviteUserDTO
from TeamSPBackend.account.models import Account


@require_http_methods(['POST', 'GET'])
@check_user_login
def invitation_router(request, *args, **kwargs):
    if request.method == 'POST':
        return add_invitation(request)
    elif request.method == 'GET':
        return get_invitation(request)
    return HttpResponseNotAllowed(['POST'])


@check_body
def add_invitation(request, body, *args, **kwargs):
    """
    TODO: check email in account
    TODO: send email

    :param body:
    :param request:
    :return:
    """
    print(body)
    invitations = list()

    user = request.session.get('user')
    user_id = user['id']

    timestamp = int(now().timestamp())

    expired = timestamp + 60 * 60 * 24 * 7
    invite_users = body['users']
    invite_list = list()
    failed_list = list()

    for invite_user in invite_users:
        invite = InviteUserDTO()
        body_extract(invite_user, invite)
        if not invite.not_empty():
            resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
            return make_json_response(HttpResponse, resp)
        invite_list.append(invite)

    for invite_user in invite_list:
        if not invite_user.validate():
            failed_list.append(dict(
                email=invite_user.email,
                first_name=invite_user.first_name,
                last_name=invite_user.last_name,
                status=InvitationRespCode.invalid_email.value.key,
                message=InvitationRespCode.invalid_email.value.msg,
            ))
            continue

        if Invitation.objects.filter(email=invite_user.email, status__lte=InvitationStatus.accepted.value.key).exists()\
                or Account.objects.filter(email=invite_user.email, status=Status.valid.value.key).exists():
            failed_list.append(dict(
                email=invite_user.email,
                first_name=invite_user.first_name,
                last_name=invite_user.last_name,
                status=InvitationRespCode.existed.value.key,
                message=InvitationRespCode.existed.value.msg,
            ))
            continue

        key = ''.join([''.join(random.sample(string.ascii_letters + string.digits, 8)) for i in range(4)])
        invitation = Invitation(key=key, first_name=invite_user.first_name, last_name=invite_user.last_name,
                                email=invite_user.email, operator=user_id, create_date=timestamp, expired=expired,
                                status=InvitationStatus.waiting.value.key)
        invitations.append(invitation)

    try:
        with transaction.atomic():
            for invite in invitations:
                invite.save()
    except Exception as e:
        print(e)
        resp = init_http_response(RespCode.server_error.value.key, RespCode.server_error.value.msg)
        return make_json_response(HttpResponse, resp)

    data = dict(
        failed=failed_list,
    )
    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    resp['data'] = data
    return make_json_response(HttpResponse, resp)


def get_invitation(request):
    """
    TODO: update expired status

    :param request:
    :param subject_id:
    :return:
    """

    user = request.session.get('user')
    user_id = user['id']

    finished = request.GET.get('finished', None)
    offset = int(request.GET.get('offset', 0))
    has_more = 0

    kwargs = dict(
        operator=user_id,
    )
    if finished is not None:
        if int(finished) == 0:
            kwargs['status__lt'] = InvitationStatus.accepted.value.key
        else:
            kwargs['status__gte'] = InvitationStatus.accepted.value.key

    kwargs_update = dict(
        expired=int(now().timestamp()),
        status=InvitationStatus.waiting.value.key,
    )
    Invitation.objects.filter(**kwargs_update).update(status=InvitationStatus.expired.value.key)

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
                status=get_message(InvitationStatus.__members__, invitation.status),
            ) for invitation in invitations
        ],
        offset=offset,
        has_more=has_more
    )

    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    resp['data'] = data
    return make_json_response(HttpResponse, resp)
