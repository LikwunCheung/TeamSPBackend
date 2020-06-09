# -*- coding: utf-8 -*-

import ujson

from django.http.response import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.utils.timezone import now

from TeamSPBackend.common.utils import make_json_response, init_http_response, check_user_login
from TeamSPBackend.common.choices import RespCode, Roles, Status
from TeamSPBackend.subject.models import Subject
from TeamSPBackend.account.models import User

SINGLE_PAGE_LIMIT = 20


@require_http_methods(['POST', 'GET'])
@check_user_login
def subject_router(request, *args, **kwargs):
    subject_id = None
    for arg in args:
        if isinstance(arg, dict):
            subject_id = arg.get('id', None)
    if request.method == 'POST':
        return add_subject(request)
    elif request.method == 'GET':
        if not subject_id:
            return multi_get_subject(request)
        return get_subject(request, subject_id)
    return HttpResponseNotAllowed(['POST'])


def get_subject(request, subject_id: int):
    """
    Get certain subject

    :param request:
    :param subject_id:
    :return:
    """
    subject = Subject.objects.get(subject_id=subject_id)
    coordinator = User.objects.get(user_id=subject.coordinator_id) if subject.coordinator_id else None
    if not subject or not coordinator:
        resp = init_http_response(RespCode.invalid_parameter, RespCode.RespCodeChoice.invalid_parameter)
        return make_json_response(HttpResponseBadRequest, resp)

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
        teams=[],
        status=subject.status,
    )

    resp = init_http_response(RespCode.success, RespCode.RespCodeChoice.success)
    resp['data'] = data
    return make_json_response(HttpResponse, resp)


def multi_get_subject(request):
    """

    :param request:
    :return:
    """

    ids = request.POST.get('ids', [])
    code = request.POST.get('code', '')
    name = request.POST.get('name', '')
    offset = int(request.POST.get('offset', 0))
    has_more = 0

    query_set = dict()
    if ids:
        query_set['subject_id__in'] = ids
    if code:
        query_set['subject_code__contains'] = code
    if name:
        query_set['name__contains'] = name
    subjects = Subject.objects.filter(query_set).order_by('subject_id')[offset: offset + SINGLE_PAGE_LIMIT + 1]
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
        resp = init_http_response(RespCode.success, RespCode.RespCodeChoice.success)
        resp['data'] = data
        return make_json_response(HttpResponse, resp)

    coord_set = set()
    for subject in subjects:
        coord_set.add(subject.coordinator_id)
    query_set = dict(
        user_id__in=list(coord_set),
        status=Status.valid,
    )
    coordinators = User.objects.filter(query_set)
    coord_dict = dict()
    for coordinator in coordinators:
        coord_dict[coordinator.user_id] = coordinator

    data = dict(
        subjects=[dict(
            id=subject.subject_id,
            code=subject.subject_code,
            coordinator=dict(
                id=subject.coordinator_id,
                name=coord_dict[subject.coordinator_id].get_name(),
                email=coord_dict[subject.coordinator_id].email,
                join_date=coord_dict[subject.coordinator_id].create_date,
                status=coord_dict[subject.coordinator_id].status,
            ),
            status=subject.status,
        ) for subject in subjects],
        has_more=has_more,
        offset=offset,
    )

    resp = init_http_response(RespCode.success, RespCode.RespCodeChoice.success)
    resp['data'] = data
    return make_json_response(HttpResponse, resp)

        
def add_subject(request):
    """

    :param request:
    :return:
    """
    subject_code = request.POST.get('code', '')
    subject_name = request.POST.get('name', '')
    coordinator_id = int(request.POST.get('coordinator_id', 0))

    if not subject_code or not subject_name or coordinator_id == 0:
        resp = init_http_response(RespCode.invalid_parameter, RespCode.RespCodeChoice.invalid_parameter)
        return make_json_response(HttpResponseBadRequest, resp)

    subject = Subject(subject_code=subject_code, subject_name=subject_name, coordinator_id=coordinator_id,
                      create_date=int(now().timestamp()), status=Status.valid)
    subject.save()

    resp = init_http_response(RespCode.success, RespCode.RespCodeChoice.success)
    return make_json_response(HttpResponse, resp)


@require_http_methods(['POST'])
@check_user_login
def update_subject(request, *args, **kwargs):
    """

    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    subject_id = None
    for arg in args:
        if isinstance(arg, dict):
            subject_id = arg.get('id', None)

    if not subject_id:
        resp = init_http_response(RespCode.invalid_parameter, RespCode.RespCodeChoice.invalid_parameter)
        return make_json_response(HttpResponseBadRequest, resp)

    subject_code = request.POST.get('code', '')
    subject_name = request.POST.get('name', '')
    coordinator_id = int(request.POST.get('coordinator_id', 0))

    subject = Subject.objects.get(subject_id=subject_id)
    if not subject:
        resp = init_http_response(RespCode.invalid_parameter, RespCode.RespCodeChoice.invalid_parameter)
        return make_json_response(HttpResponseBadRequest, resp)

    subject.subject_code = subject_code
    subject.subject_name = subject_name
    subject.coordinator_id = coordinator_id
    subject.save()

    resp = init_http_response(RespCode.success, RespCode.RespCodeChoice.success)
    return make_json_response(HttpResponse, resp)


@require_http_methods(['POST'])
@check_user_login
def delete_subject(request, *args, **kwargs):
    """

    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    subject_id = None
    for arg in args:
        if isinstance(arg, dict):
            subject_id = arg.get('id', None)

    if not subject_id:
        resp = init_http_response(RespCode.invalid_parameter, RespCode.RespCodeChoice.invalid_parameter)
        return make_json_response(HttpResponseBadRequest, resp)

    subject = Subject.objects.get(subject_id=subject_id)
    if not subject:
        resp = init_http_response(RespCode.invalid_parameter, RespCode.RespCodeChoice.invalid_parameter)
        return make_json_response(HttpResponseBadRequest, resp)

    subject.status = Status.invalid
    subject.save()

    resp = init_http_response(RespCode.success, RespCode.RespCodeChoice.success)
    return make_json_response(HttpResponse, resp)
