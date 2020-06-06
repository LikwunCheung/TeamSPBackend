# -*- coding: utf-8 -*-

import ujson

from django.http.response import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.utils.timezone import now
from django.contrib.sessions.models import Session

from TeamSPBackend.common.utils import make_json_response, init_http_response
from TeamSPBackend.subject.models import Subject
from TeamSPBackend.account.models import User


@require_http_methods(['POST', 'GET'])
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


def get_subject(request, id):
    """

    :param request:
    :param id:
    :return:
    """
    try:
        subject_id = id
        subject = Subject.objects.get(subject_id=subject_id)
        data = {'id': subject.subject_id,
        'name': subject.subject_name,
        'code': subject.subject_code,
        'coordinator': subject.coordinator_id,
        # 'supervisors': Supervisor.objects.filter(subject_id = subject_id),
        # 'projects': Project.objects.filter(subject_id = subject_id),
        'status': subject.status
        }
        resp = {'code': 0, 'msg': 'The subject data got','data': data}
        return HttpResponse(ujson.dumps(resp), content_type="application/json")
    except Subject.DoesNotExist:
        subject = None
        resp = {'code': -1, 'msg': 'The subject is not found'}
        return HttpResponse(ujson.dumps(resp), content_type="application/json")


# get multiple subjects
def multi_get_subject(request, subId):
    substring = subId
    subjects = Subject.objects.filter(Q(subject_id__contains=substring))
    data = list(subjects.values())
    resp = {'code': 0, 'msg': 'The subject data got','data': data}
    return HttpResponse(ujson.dumps(resp), content_type="application/json")
    
        
# add a subject
def add_subject(request):
    subject_code = request.POST.get('code')
    subject_name = request.POST.get('name')
    coordinator_id = request.POST.get('coordinator_id')
    subject = Subject(subject_code=subject_code, subject_name=subject_name, coordinator_id = coordinator_id, create_date=int(now().timestamp()))
    subject.save()
    resp = {'code': 0, 'msg': 'The subject is added.'}
    return HttpResponse(ujson.dumps(resp), content_type="application/json")


# update a subject
def update_subject(request, id):
    subject_id = id
    subject_code = request.POST.get('code')
    subject_name = request.POST.get('name')
    coordinator_id = request.POST.get('coordinator_id')
    try:
        subject = Subject.objects.get(subject_id = subject_id)
        subject.subject_code = subject_code
        subject.subject_name = subject_name
        subject.coordinator_id = coordinator_id
        subject.save()
        resp = {'code': 0, 'msg': 'The subject is updated.'}
        return HttpResponse(ujson.dumps(resp), content_type="application/json")
    except Subject.DoesNotExist:
        subject = None
        resp = {'code': -1, 'msg': 'This subject is not found.'}
        return HttpResponse(ujson.dumps(resp), content_type="application/json")


# delete a subject
def delete_subject(request, id):
    subject_id = id
    try:
        subject = Subject.objects.filter(subject_id = subject_id)
        subject.delete()
        resp = {'code': 0, 'msg': 'This subject is deleted.'}
        return HttpResponse(ujson.dumps(resp), content_type="application/json")
    except Subject.DoesNotExist:
        subject = None
        resp = {'code': -1, 'msg': 'This subject is not found.'}
        return HttpResponse(ujson.dumps(resp), content_type="application/json")
