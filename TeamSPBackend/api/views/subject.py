# -*- coding: utf-8 -*-

import ujson

from django.http.response import JsonResponse,HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.utils.timezone import now
from django.contrib.sessions.models import Session

from TeamSPBackend.common.utils import make_json_response, init_http_response
from TeamSPBackend.account.models import Account
from TeamSPBackend.subject.models import Subject
from TeamSPBackend.supervisor.models import Supervisor
from TeamSPBackend.project.models import Project

@require_http_methods(['GET', 'DELETE', 'PUT', 'POST'])
def subject_router(request):
    if request.method == 'GET':
        return getSubject(request)
    if request.method == 'POST':
        return addSubject(request)
    if request.method == 'PUT':
        return updateSubject(request)
    if request.method == 'DELETE':
        return deleteSubjects(request)

# return the subject by querying the subject id
def getSubject(request):
    subject_id = request.POST.get['id']
    try:
        subject = Subject.objects.get(subject_id = subject_id)
        data = {'id': subject.subject_id,
        'name': subject.subject_name,
        'code': subject.subject_code,
        'coordinator': subject.coordinator_id,
        'supervisors': Supervisor.objects.filter(subject_id = subject_id),
        'projects': Project.objects.filter(subject_id = subject_id),
        'status': subject.status
        }
        resp = {'code': 0, 'msg': 'The subject data got','data': data}
        return HttpResponse(ujson.dumps(resp), content_type="application/json")
    except Subject.DoesNotExist:
        subject = None
        resp = {'code': -1, 'msg': 'The subject is not found'}
        return HttpResponse(ujson.dumps(resp), content_type="application/json")

# get multiple subjects
# format:{"num": "2", "1": "101", "2": "102"}
def multiGetSubject(request):
    ids = ujson.loads(request.body)
    numIds = ids['num']
    subjects = list()
    try:
        for id in range(numIds):
            subjects.append(Subject.objects.get(ids[id]))
        return HttpResponse(ujson.dumps(subjects))
    except Subject.DoesNotExist:
        subject = None
        return JsonResponse({'delete':'does not exist'}, status=404)
        
 # add a subject
def addSubject(request):
    subject_code = request.POST.get['code']
    subject_name = request.POST.get['name']
    coordinator_id = request.POST.get['coordinator_id']
    subject = Subject(subject_code=subject_code, subject_name=subject_name)
    subject.save()
    resp = {'code': 0, 'msg': 'The subject is added.'}
    return HttpResponse(ujson.dumps(resp), content_type="application/json")

# update a subject
def updateSubject(request):
    subject_id = request.POST.get['id']
    subject_code = request.POST.get['code']
    subject_name = request.POST.get['name']
    coordinator_id = request.POST.get['coordinator_id']
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
def deleteSubjects(request):
    subject_id = request.POST.get['id']
    try:
        subject = Subject.objects.filter(subject_id = subject_id)
        subject.delete()
        resp = {'code': 0, 'msg': 'This subject is deleted.'}
        return HttpResponse(ujson.dumps(resp), content_type="application/json")
    except Subject.DoesNotExist:
        subject = None
        resp = {'code': -1, 'msg': 'This subject is not found.'}
        return HttpResponse(ujson.dumps(resp), content_type="application/json")



##############
## NOTDONE ##
############

# @require_http_methods(['GET', 'DELETE', 'PUT'])
# def supervisorsSubject_router(request):
#     if request.method == 'GET':
#         return get_supervisors(subject_id)
    # elif request.method == 'DELETE':
    #     return delete_supervisors(subject_id)
    # elif request.method == 'PUT':
    #     return update_supervisors(subject_id)
    # return HttpResponseNotAllowed(['POST'])

#return a list of supervisors in a subject
# def get_supervisors(request):
#     subject = Subject.objects.get(subject_id = sid)
#     supervisors = subject.supervisor_ids
#     supervisors_names = {}


# def delete_supervisors(sid, supervisor_id):
#     subject = Subject.objects.get(subject_id = sid)
