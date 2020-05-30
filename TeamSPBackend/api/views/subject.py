# -*- coding: utf-8 -*-

import ujson

from django.http.response import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.utils.timezone import now
from django.contrib.sessions.models import Session

from TeamSPBackend.common.utils import make_json_response, init_http_response
from TeamSPBackend.account.models import Account
from TeamSPBackend.subject.models import Subject


@require_http_methods(['GET', 'DELETE', 'PUT'])
def subject_router(request, *args, **kwargs):
    if request.method == 'GET':
        return get_supervisors('id')
    # elif request.method == 'DELETE':
    #     return delete_supervisors(subject_id)
    # elif request.method == 'PUT':
    #     return update_supervisors(subject_id)
    # return HttpResponseNotAllowed(['POST'])


def get_supervisors(id):
    subject = Subject.objects.get(subject_id=id)


@require_http_methods(['GET'])
def subject_get(request, subject_id):
    subject = Subject.objects.filter(subject_id=subject_id)
    result = [dict(
        subject_id=subject.subject_id,
        subject_code=subject.subject_code,
        subject_name=subject.subject_name,
        coordinator_id=subject.coordinator_id,
        supervisors=subject.supervisors,
        status=subject.status)]

    resp = init_http_success()
    resp['data'] = result
    return make_json_response(HttpResponse, resp)


@require_http_methods(['POST'])
def subject_add(request):


@require_http_methods(['POST'])
def subject_update(request):


@require_http_methods(['POST'])
def subject_delete(request):
