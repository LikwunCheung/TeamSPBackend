# -*- coding: utf-8 -*-

import ujson

from django.http.response import JsonResponse,HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.utils.timezone import now
from django.contrib.sessions.models import Session

from TeamSPBackend.common.utils import make_json_response, init_http_response
from TeamSPBackend.account.models import Account
from TeamSPBackend.subject.models import Subject

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
    sid = ujson.loads(request.body)
    try:
        subject = Subject.objects.get(subject_id = sid)
        return HttpResponse(ujson.dumps(subject))
    except Subject.DoesNotExist:
        subject = None
        return JsonResponse({'delete':'does not exist'}, status=404)

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
    subjectData = ujson.loads(request.body)
    subject_code = subjectData['subject_code']
    subject_name = subjectData['subject_name']
    create_date = timestamp = int(now().timestamp())
    status = subjectData['status']
    subject = Subject(subject_code=subject_code, subject_name=subject_name, create_date=create_date, status=status)
    subject.save()
    return JsonResponse({'add':'success'}, status=200)

# update a subject
def updateSubject(request):
    subjectData = ujson.loads(request.body)
    subject_id = subjectData['subject_id']
    subject_code = subjectData['subject_code']
    subject_name = subjectData['subject_name']
    create_date = timestamp = int(now().timestamp())
    status = subjectData['status']
    subject = Subject.objects.get(subject_id = subject_id)
    subject.subject_code = subject_code
    subject.subject_name = subject_name
    subject.create_date = create_date
    subject.status = status
    subject.save()
    return JsonResponse({'update':'success'}, status=200)

# delete a subject
def deleteSubjects(request):
    sid = ujson.loads(request.body)
    try:
        subject = Subject.objects.filter(subject_id = sid)
        subject.delete()
        return JsonResponse({'delete':'success'}, status=200)
    except Subject.DoesNotExist:
        subject = None
        return JsonResponse({'delete':'does not exist'}, status=404)



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
