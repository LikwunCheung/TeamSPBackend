import json

from django.shortcuts import render
from django.http import HttpResponse
from django.utils.timezone import now
from django.views.decorators.http import require_http_methods
from TeamSPBackend.common.utils import check_body
from TeamSPBackend.account.models import Account
from TeamSPBackend.team.models import Team, Student, TeamMember
from TeamSPBackend.csv_data.csvRead import read_csv

"""
Create team
Method: Post
Request: csv_file
"""


def create_team(request, sid):
    file = request.FILES.get('file')
    print(file)
    read_csv(file, sid)
    resp = {'code': 0, 'msg': 'create successfully'}
    return HttpResponse(json.dumps(resp), content_type="application/json")



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


def get_teams(request):
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
