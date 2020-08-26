import json

from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.http import HttpResponse, HttpResponseNotAllowed
from django.utils.timezone import now
from django.views.decorators.http import require_http_methods
from TeamSPBackend.common.utils import check_body, check_user_login, make_json_response, init_http_response
from TeamSPBackend.common.choices import RespCode, Roles, Status
from TeamSPBackend.account.models import Account
from TeamSPBackend.team.models import Team, Student, TeamMember
from TeamSPBackend.csv_data.csvRead import read_csv
from TeamSPBackend.subject.models import Subject
from TeamSPBackend.account.models import User
from django.db.models import ObjectDoesNotExist


@require_http_methods(['POST', 'GET'])
@check_user_login
def team_router(request, *args, **kwargs):
    subject_id = None
    supervisor_id = None
    team_id = None
    for arg in args:
        if isinstance(arg, dict):
            subject_id = arg.get('subject_id', None)
            supervisor_id = arg.get('supervisor_id', None)
            team_id = arg.get('team_id', None)
    if request.method == 'POST':
        if team_id:
            return assign_supervisor(request, team_id)  # done
        return create_team(request, supervisor_id)  # todo
    elif request.method == 'GET':
        if team_id:
            return get_team_members(request, team_id)  # done
        elif not supervisor_id:
            return get_teams(request, subject_id)  # todo
        return get_teams(request, subject_id, supervisor_id)  #todo
    return HttpResponseNotAllowed(['POST'])



"""
Create team from Atalassian 
Method: Post
Request: csv_file
"""


def create_team(request, subject_id):
    file = request.FILES.get('file')
    print(file)
    read_csv(file, subject_id)
    resp = {'code': 0, 'msg': 'create successfully'}
    return HttpResponse(json.dumps(resp), content_type="application/json")

#
# def createTeam(request):
#     try:
#         name = request.POST.get('name')
#         project_name = request.POST.get('project_name')
#         description = request.POST.get('description')
#         # supervisor = Account.objects.get(username = request.POST.get('supervisor'))
#         supervisor_id = request.POST.get('supervisor_id')
#         # member_id = request.POST.get('member_id')
#         duration = request.POST.get('duration')
#         timestamp = int(now().timestamp())
#         expired = timestamp + 60 * 60 * 24 * int(duration)
#         team = Team(name=name, project_name=project_name, description=description, supervisor_id=supervisor_id,
#                     create_date=timestamp, expired=expired)
#         team.save()
#         resp = {'code': 0, 'msg': 'create successfully'}
#         return HttpResponse(json.dumps(resp), content_type="application/json")
#     except:
#         resp = {'code': -1, 'msg': 'error'}
#         return HttpResponse(json.dumps(resp), content_type="application/json")


"""
Create relation between team and members
Method: Post
Request: team_id, student_id
"""


def team_member(request):
    try:
        student_id = request.POST.get('student_id')
        team_id = request.POST.get('team_id')
        if TeamMember.objects.filter(team_id=team_id, student_id=student_id).exists():
            resp = {'code': 0, 'msg': 'exist'}
            return HttpResponse(json.dumps(resp), content_type="application/json")
        else:
            TeamMember(student_id=student_id, team_id=team_id).save()
            resp = {'code': 1, 'msg': 'add student to team'}
            return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


"""
Get team information
Method: Get
Request: team_ids
"""


def get_teams(request, subject_id: int, supervisor_id: int):
    try:
        ids = request.GET.getlist('ids', [])
        teams = []
        for team_id in ids:
            team = Team.objects.get(team_id=team_id)
            supervisor = Account.objects.get(account_id=team.supervisor_id)
            supervisor_data = {
                'id': supervisor.account_id,
                'name': supervisor.username,
                'email': supervisor.email
            }
            t_members = TeamMember.objects.filter(team_id=team_id)
            member_datas = []
            for t_member in t_members:
                member_id = t_member.student_id
                member = Student.objects.get(student_id=member_id)
                member_data = {
                    'id': member_id,
                    'name': member.name,
                    'email': member.email
                }
                member_datas.append(member_data)

            team_data = {
                'id': team.team_id,
                'name': team.name,
                'description': team.description,
                'supervisor': supervisor_data,
                'member': member_datas,
                'create_date': team.create_date,
                'expired': team.expired
            }
            teams.append(team_data)
        body = {
            'teams': teams

        }
        return HttpResponse(json.dumps(body), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")

"""
Assign secondary supervisor for a specific team
Method: Post
Request: secondary_supervisor_id, team_id
"""


def assign_supervisor(request, team_id: int):
    """
            Post secondary_supervisor_id

            :param request:
            :param team_id:
            :return:
            """
    try:
        secondary_supervisor_id = request.GET('secondary_supervisor_id', None)
        team = Team.objects.get(team_id=team_id)
    except ObjectDoesNotExist as e:
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponseBadRequest, resp)
    if secondary_supervisor_id:
        team.secondary_supervisor_id=secondary_supervisor_id
        team.save()
        resp = {'code': 0, 'msg': 'create successfully'}
        return HttpResponse(json.dumps(resp), content_type="application/json")



def get_team_members(request, team_id: int):
    """
        Get certain team members

        :param request:
        :param team_id:
        :return:
        """

    try:
        team = Team.objects.get(team_id=team_id)
        team_members = TeamMember.objects.get(team_id=team_id)
        supervisor = User.objects.get(user_id=team.supervisor_id)
        secondary_supervisor = User.objects.get(user_id=team.secondary_supervisor_id)
    except ObjectDoesNotExist as e:
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponseBadRequest, resp)

    members = []

    if supervisor:
        supervisor_data = {
            'supervisor_first_name', supervisor.first_name,
            'supervisor_last_name', supervisor.last_name,
            'supervisor_email', supervisor.email
        }
        members.append(supervisor_data)

    if secondary_supervisor:
        secondary_supervisor_data = {
            'secondary_supervisor_first_name', secondary_supervisor.first_name,
            'secondary_supervisor_last_name', secondary_supervisor.last_name,
            'secondary_supervisor_email', secondary_supervisor.email,

        }
        members.append(secondary_supervisor_data)

    for member in team_members:
        student = Student.objects.get(id=member.student_id)
        member_data = {
            'student_id': student.student_id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'student_email': student.email
        }
        members.append(member_data)

    data = {
        'team_members': members
    }

    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    resp['data'] = data
    return make_json_response(HttpResponse, resp)
