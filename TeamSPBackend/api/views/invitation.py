# -*- coding: utf-8 -*-

import random
import string

from django.http.response import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.db import transaction

from TeamSPBackend.common import smtp_thread
from TeamSPBackend.common.utils import make_json_response, init_http_response, check_user_login, check_body, body_extract, mills_timestamp, get_invitation_link
from TeamSPBackend.common.choices import InvitationStatus, RespCode, InvitationRespCode, Status, get_message, Roles
from TeamSPBackend.common.config import SINGLE_PAGE_LIMIT, PATTERN_COORDINATOR, PATTERN_URL
from TeamSPBackend.invitation.models import Invitation
from TeamSPBackend.account.models import Account, User
from TeamSPBackend.api.dto.dto import InviteAcceptDTO


@require_http_methods(['POST', 'GET'])
@check_user_login
def invitation_router(request, *args, **kwargs):
    print(request.COOKIES)
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

    user = request.session.get('user')
    user_id = user['id']

    timestamp = mills_timestamp()

    expired = timestamp + 1000 * 60 * 60 * 24 * 1
    invite_emails = body['emails']
    template = body['template']
    failed_list = list()
    invitations = list()

    if PATTERN_COORDINATOR not in template or PATTERN_URL not in template:
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponse, resp)

    for email in invite_emails:
        if Invitation.objects.filter(email=email, status__lte=InvitationStatus.accepted.value.key).exists() or \
                Account.objects.filter(email=email, status=Status.valid.value.key).exists():
            failed_list.append(dict(
                email=email,
                status=InvitationRespCode.existed.value.key,
                message=InvitationRespCode.existed.value.msg,
            ))
            continue

        key = ''.join([''.join(random.sample(string.ascii_letters + string.digits, 8)) for i in range(4)])
        content = str(template).replace('<Coordinator>', user['name']).replace('<URL>', get_invitation_link(key))
        print(content)
        invitation = Invitation(key=key, email=email, operator=user_id, create_date=timestamp, expired=expired,
                                template=content, status=InvitationStatus.waiting.value.key)
        invitations.append(invitation)

    try:
        with transaction.atomic():
            for invite in invitations:
                invite.save()
        for invite in invitations:
            smtp_thread.put_task(invite.invitation_id, user['name'], invite.email, invite.template)
    except Exception as e:
        print(e)
        resp = init_http_response(RespCode.server_error.value.key, RespCode.server_error.value.msg)
        return make_json_response(HttpResponse, resp)

    data = dict(
        invitation=[dict(
            email=invite.email,
            status=invite.status,
            template=invite.template,
            message=get_message(InvitationStatus.__members__, invite.status),
            expired=invite.expired,
        ) for invite in invitations],
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
        expired=mills_timestamp(),
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


@require_http_methods(['POST'])
@check_body
def invite_accept(request, body, *args, **kwargs):
    """
    Accept Invitation and Create Account (WIP)
    Method: Post
    Request: key, username, password
    """
    print(body)

    invite_accept_dto = InviteAcceptDTO()
    body_extract(body, invite_accept_dto)

    if not invite_accept_dto.not_empty():
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponse, resp)

    if Account.objects.filter(username=invite_accept_dto.username).exists():
        resp = init_http_response(RespCode.account_existed.value.key, RespCode.account_existed.value.msg)
        return make_json_response(HttpResponse, resp)

    invitation = Invitation.objects.get(key=invite_accept_dto.key, status=InvitationStatus.sent.value.key)
    if invitation is None:
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponse, resp)

    timestamp = mills_timestamp()
    data = dict()
    try:
        with transaction.atomic():
            invite_accept_dto.encrypt()
            account = Account(username=invite_accept_dto.username, password=invite_accept_dto.md5,
                              email=invitation.email, status=Status.valid.value.key, create_date=timestamp,
                              update_date=timestamp)
            account.save()

            data['account_id'] = account.account_id
            user = User(account_id=account.account_id, username=invite_accept_dto.username,
                        first_name=invite_accept_dto.first_name, last_name=invite_accept_dto.last_name,
                        role=Roles.supervisor.value.key, status=Status.valid.value.key,
                        create_date=timestamp, update_date=timestamp, email=invitation.email)
            user.save()

            invitation.status = InvitationStatus.accepted.value.key
            invitation.accept_reject_date = timestamp
            invitation.save()
    except Exception as e:
        print(e)
        resp = init_http_response(RespCode.server_error.value.key, RespCode.server_error.value.msg)
        return make_json_response(HttpResponse, resp)

    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    resp['data'] = data
    return make_json_response(HttpResponse, resp)
