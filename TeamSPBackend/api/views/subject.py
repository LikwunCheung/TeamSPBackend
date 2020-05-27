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
def supervisorsSubject_router(request, subject_id):
    if request.method == 'GET':
        return get_supervisors(subject_id)
    # elif request.method == 'DELETE':
    #     return delete_supervisors(subject_id)
    # elif request.method == 'PUT':
    #     return update_supervisors(subject_id)
    # return HttpResponseNotAllowed(['POST'])


def get_supervisors(id):
    subject = Subject.objects.get(subject_id = id)
