# -*- coding: utf-8 -*-

import ujson

from django.http.response import JsonResponse,HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.utils.timezone import now
from django.contrib.sessions.models import Session
from django.db.models import Q
from TeamSPBackend.common.utils import make_json_response, init_http_response
from TeamSPBackend.subject.models import Subject
from TeamSPBackend.supervisor.models import Supervisor
from TeamSPBackend.project.models import Project

# return the subject by querying the subject id
def getSubject(request, id):
    
    try:
        subject_id = id
        subject = Subject.objects.get(subject_id = subject_id)
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
def multiGetSubject(request, subId):
    substring = subId
    subjects = Subject.objects.filter(Q(subject_id__contains=substring))
    data = list(subjects.values())
    resp = {'code': 0, 'msg': 'The subject data got','data': data}
    return HttpResponse(ujson.dumps(resp), content_type="application/json")
    
        
 # add a subject
def addSubject(request):
    subject_code = request.POST.get('code')
    subject_name = request.POST.get('name')
    coordinator_id = request.POST.get('coordinator_id')
    subject = Subject(subject_code=subject_code, subject_name=subject_name, coordinator_id = coordinator_id, create_date=int(now().timestamp()))
    subject.save()
    resp = {'code': 0, 'msg': 'The subject is added.'}
    return HttpResponse(ujson.dumps(resp), content_type="application/json")

# update a subject
def updateSubject(request, id):
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
def deleteSubjects(request, id):
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
