# -*- coding: utf-8 -*-

import ujson

from django.http.response import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.db.models import ObjectDoesNotExist

from TeamSPBackend.common.utils import make_json_response, init_http_response, check_user_login, check_body, body_extract, mills_timestamp
from TeamSPBackend.common.choices import RespCode, Roles, Status, get_keys
from TeamSPBackend.common.config import SINGLE_PAGE_LIMIT
from TeamSPBackend.subject.models import Subject
from TeamSPBackend.account.models import User
from TeamSPBackend.api.dto.dto import *
from TeamSPBackend.team.models import Team


@require_http_methods(['POST', 'GET'])
@check_user_login()
def subject_router(request, *args, **kwargs):
    subject_id = None
    if isinstance(kwargs, dict):
        subject_id = kwargs.get('id', None)
    if request.method == 'POST':
        return add_subject(request)
    elif request.method == 'GET':
        if not subject_id:
            return multi_get_subject(request)
        return get_subject(request, subject_id)
    return HttpResponseNotAllowed(['POST', 'GET'])


def get_subject(request, subject_id: int):
    """
    Get certain subject

    :param request:
    :param subject_id:
    :return:
    """

    try:
        subject = Subject.objects.get(subject_id=subject_id)
        print(subject)
        coordinator = User.objects.get(user_id=subject.coordinator_id) if subject.coordinator_id else None
        teams = Team.objects.filter(subject_code=subject.subject_code)
    except ObjectDoesNotExist as e:
        print(e)
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponse, resp)

    data = dict(
        id=subject.subject_id,
        code=subject.subject_code,
        name=subject.name,
        coordinator=dict(
            id=coordinator.user_id,
            name=coordinator.get_name(),
            email=coordinator.email,
            join_date=coordinator.create_date,
            status=coordinator.status,
        ),
        supervisors=[],
        teams=[team.team_id for team in teams],
        status=subject.status,
    )

    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    resp['data'] = data
    return make_json_response(HttpResponse, resp)


@check_user_login()
def multi_get_subject(request, *args, **kwargs):
    """
    Multi get subject

    :param request:
    :return:
    """

    ids = request.GET.get('ids', None)
    code = request.GET.get('code', None)
    name = request.GET.get('name', None)
    offset = int(request.POST.get('offset', 0))
    has_more = 0

    kwargs = dict()
    if ids:
        kwargs['subject_id__in'] = [int(x) for x in ids.split(',')]
    if code:
        kwargs['subject_code__contains'] = code
    if name:
        kwargs['name__contains'] = name

    subjects = Subject.objects.filter(**kwargs).order_by('subject_code')[offset: offset + SINGLE_PAGE_LIMIT + 1]

    if len(subjects) > SINGLE_PAGE_LIMIT:
        subjects = subjects[: SINGLE_PAGE_LIMIT]
        has_more = 1
    offset += len(subjects)

    if len(subjects) == 0:
        data = dict(
            subjects=[],
            has_more=has_more,
            offset=offset,
        )
        resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return make_json_response(HttpResponse, resp)

    coord_set = set()
    for subject in subjects:
        coord_set.add(subject.coordinator_id)
    kwargs = dict(
        user_id__in=list(coord_set),
        status=Status.valid.value.key,
    )
    coordinators = User.objects.filter(**kwargs)
    coord_dict = dict()
    for coordinator in coordinators:
        coord_dict[coordinator.user_id] = coordinator

    data = dict(
        ids=[x.subject_id for x in subjects],
        has_more=has_more,
        offset=offset,
    )

    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    resp['data'] = data
    return make_json_response(HttpResponse, resp)


@check_user_login(get_keys([Roles.coordinator, Roles.admin]))
@check_body
def add_subject(request, body, *args, **kwargs):
    """

    :param request:
    :return:
    """
    add_subject_dto = AddSubjectDTO()
    body_extract(body, add_subject_dto)

    # if the parameter is not sufficient
    if not add_subject_dto.not_empty():
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponseBadRequest, resp)

    # if the subject code existed
    if Subject.objects.filter(subject_code=add_subject_dto.code).exists():
        resp = init_http_response(RespCode.subject_existed.value.key, RespCode.subject_existed.value.msg)
        return make_json_response(HttpResponseBadRequest, resp)

    if not User.objects.filter(user_id=add_subject_dto.coordinator_id).exists():
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponseBadRequest, resp)

    subject = Subject(subject_code=add_subject_dto.code, name=add_subject_dto.name,
                      coordinator_id=add_subject_dto.coordinator_id, create_date=mills_timestamp(),
                      status=Status.valid.value.key)
    subject.save()

    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    return make_json_response(HttpResponse, resp)


@require_http_methods(['POST'])
@check_user_login(get_keys([Roles.coordinator, Roles.admin]))
@check_body
def update_subject(request, body, *args, **kwargs):
    """

    :param body:
    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    subject_id = kwargs.get('id')

    if not subject_id:
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponse, resp)

    add_subject_dto = AddSubjectDTO()
    body_extract(body, add_subject_dto)

    try:
        subject = Subject.objects.get(subject_id=subject_id, status=Status.valid.value.key)

        if add_subject_dto.code is not None:
            subject.subject_code = add_subject_dto.code
        if add_subject_dto.name is not None:
            subject.name = add_subject_dto.name
        if add_subject_dto.coordinator_id is not None:
            subject.coordinator_id = add_subject_dto.coordinator_id
        subject.save()
    except ObjectDoesNotExist as e:
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponse, resp)

    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    return make_json_response(HttpResponse, resp)


@require_http_methods(['POST'])
@check_user_login(get_keys([Roles.coordinator, Roles.admin]))
def delete_subject(request, *args, **kwargs):
    """

    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    subject_id = kwargs.get('id')

    if not subject_id:
        print("fuck")
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponse, resp)

    try:
        subject = Subject.objects.get(subject_id=subject_id)
    except ObjectDoesNotExist as e:
        print("fuck two")
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponse, resp)

    subject.status = Status.invalid.value.key
    subject.save()

    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    return make_json_response(HttpResponse, resp)
