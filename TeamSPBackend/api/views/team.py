import json
from TeamSPBackend.common.config import SINGLE_PAGE_LIMIT
from django.http.response import HttpResponseBadRequest
from django.http import HttpResponse, HttpResponseNotAllowed
from django.utils.timezone import now
from django.views.decorators.http import require_http_methods
from TeamSPBackend.common.utils import check_user_login, make_json_response, init_http_response, check_body
from TeamSPBackend.common.choices import RespCode, Roles
from TeamSPBackend.account.models import Account
from TeamSPBackend.api.views.confluence.confluence import get_team_members
from TeamSPBackend.team.models import Team, Student, TeamMember
from TeamSPBackend.subject.models import Subject
from TeamSPBackend.account.models import User
from django.db.models import ObjectDoesNotExist


@require_http_methods(['POST', 'GET'])
@check_user_login
def team_router(request, *args):
    team_id = None
    for arg in args:
        if isinstance(arg, dict):
            team_id = arg.get('team_id', None)
    if request.method == 'POST':
        if team_id:
            # Assign secondary supervisor for a specific team
            return update_team(request, team_id)  # done
        # Import team from confluence with supervisor_id
        return import_team(request)
        # Todo: might need to change for retrieving confluence data / front-end request with team info
    elif request.method == 'GET':
        if team_id:
            # Get a specific team information
            return get_team_members(request, team_id)  # done
        # Get teams information
        return multi_get_team(request)  # done
    return HttpResponseNotAllowed(['POST'])


"""
Import team from confluence with supervisor_id

Method: POST
Url: localhost:8000/api/v1/team
Params: 
Request: team, subject, year, project
        {
            "team":                     "SWEN90013_2020_SP",
            "subject":                  "SWEN90013",
            "year":                     "2020",
            "project":                  "SP"
        }
"""


def import_team(request):
    name = request.POST.get('team', None)
    subject = request.POST.get('subject', None)
    year = request.POST.get('year', None)
    project = request.POST.get('project', None)
    team_members = get_team_members(request, name)

    if Team.objects.filter(name=name, subject_id=subject, year=year, project_name=project).exists():
        resp = {'code': 0, 'msg': 'exist'}
        return HttpResponse(json.dumps(resp), content_type="application/json")
    else:
        team = Team(name=name, subject_id=subject, year=year, project_name=project)
        team.save()
        team_id = team.team_id
        for member in team_members:
            student = Student(fullname=member.get('name'), email=member.get('email'))
            student.save()
            student_id = student.student_id
            import_team_member(team_id, student_id)
    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    return HttpResponse(json.dumps(resp), content_type="application/json")


# Add team member records
def import_team_member(team_id, student_id):
    if TeamMember.objects.filter(team_id=team_id, student_id=student_id).exists():
        return False
    else:
        TeamMember(student_id=student_id, team_id=team_id).save()
        return True

"""
Create team from csv
Method: Post
Request: csv_file
"""


# def create_team(request, subject_id):
#     file = request.FILES.get('file')
#     print(file)
#     read_csv(file, subject_id)
#     resp = {'code': 0, 'msg': 'create successfully'}
#     return HttpResponse(json.dumps(resp), content_type="application/json")

"""
Create team from request with supervisor_id 
Method: Post
Url: localhost:8000/api/v1/team
Params: None
Request: 
            {
                "name":                #team_name,
                "description":         #team_description,
                "supervisor_id"：      #supervisor_id,
                "year"：               #year,
                "duration":            #days,
                "students":[
                    {
                        "student_id":       #student_id,
                        "student_number":   #student_number,
                        "first_name":       #first_name,
                        "last_name":        #last_name,
                        "email":            #email
                    },
                    ...
                    {
                        "student_id":       #student_id,
                        "student_number":   #student_number,
                        "first_name":       #first_name,
                        "last_name":        #last_name,
                        "email":            #email
                    }
                ]
            }
"""


def create_team(request):
    try:
        name = request.POST.get('name')
        description = request.POST.get('description')
        # supervisor = Account.objects.get(username = request.POST.get('supervisor'))
        supervisor_id = request.POST.get('supervisor_id')
        year = request.POST.get('year')
        # member_id = request.POST.get('member_id')
        # duration = request.POST.get('duration')
        project_name = request.POST.get('project_name')
        timestamp = int(now().timestamp())
        # expired = timestamp + 60 * 60 * 24 * int(duration)
        team = Team(name=name, description=description, supervisor_id=supervisor_id,
                    year=year, create_date=timestamp, project_name=project_name)
        team.save()
        resp = {'code': 0, 'msg': 'create successfully'}
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except ObjectDoesNotExist:
        resp = {'code': -1, 'msg': 'error'}
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
Get a specific team information (not needed for now)

Method: Get
Url: localhost:8000/api/v1/team/<int:team_id>
Params: team_id
Request: None
"""


# def get_team(request, team_id: int):
#     try:
#         data = []
#         team = Team.objects.get(team_id=team_id)
#
#         supervisor = Account.objects.get(account_id=team.supervisor_id)
#         supervisor_data = {
#             'supervisor_id': supervisor.account_id,
#             'first_name': supervisor.first_name,
#             'last_name': supervisor.last_name,
#             'email': supervisor.email
#         }
#
#         secondary_supervisor = Account.objects.get(account_id=team.secondary_supervisor_id)
#         secondary_supervisor_data = {
#             'secondary_supervisor_id': secondary_supervisor.account_id,
#             'first_name': secondary_supervisor.first_name,
#             'last_name': secondary_supervisor.last_name,
#             'email': secondary_supervisor.email
#         }
#
#         t_members = TeamMember.objects.filter(team_id=team_id)
#         members_data = []
#         for t_member in t_members:
#             member_id = t_member.student_id
#             member = Student.objects.get(student_id=member_id)
#             member_data = {
#                 'student_id': member_id,
#                 'first_name': member.first_name,
#                 'last_name': member.last_name,
#                 'student_email': member.email
#             }
#             members_data.append(member_data)
#
#         team_data = {
#             'id': team.team_id,
#             'name': team.name,
#             'description': team.description,
#             'subject_id': team.subject_id,
#             'year': team.year,
#             'supervisor': supervisor_data,
#             'secondary_supervisor': secondary_supervisor_data,
#             'create_date': team.create_date,
#             'expired': team.expired,
#             'member': members_data
#         }
#         data.append(team_data)
#         body = {
#             'team_data': data
#
#         }
#         return HttpResponse(json.dumps(body), content_type="application/json")
#
#     except:
#         resp = {'code': -1, 'msg': 'error'}
#         return HttpResponse(json.dumps(resp), content_type="application/json")


"""
Get teams information

Method: Get
Url: localhost:8000/api/v1/team
Params: None
Request: supervisor_id (necessary), subject_id||year (optional), team_ids (optional)
    case1:
        {
            "supervisor_id":          #supervisor_id
        }
    case2:
        {
            "supervisor_id":          #supervisor_id,
            "subject_id":             #subject_id
        }
    case3:
        {
            "supervisor_id":          #supervisor_id,
            "year":                   #year
        }
    case4:
        {
            "supervisor_id":          #supervisor_id,
            "subject_id":             #subject_id,
            "year":                   #year
        }
    case5:
        {
            "supervisor_id":          #supervisor_id,
            "team_ids":               [1, 2, 3, 4]
        }
"""


# function to return all team candidates info as a list
def get_teams_data(filtered_teams):
    teams = []
    for i in range(len(filtered_teams)):
        for team in filtered_teams[i]:
            try:
                supervisor = User.objects.get(account_id=team.supervisor_id)
                supervisor_data = {
                    'supervisor_id': supervisor.account_id,
                    'first_name': supervisor.first_name,
                    'last_name': supervisor.last_name,
                    'email': supervisor.email
                }
            except ObjectDoesNotExist:
                supervisor_data = {}
            try:
                secondary_supervisor = User.objects.get(account_id=team.secondary_supervisor_id)
                secondary_supervisor_data = {
                    'secondary_supervisor_id': secondary_supervisor.account_id,
                    'first_name': secondary_supervisor.first_name,
                    'last_name': secondary_supervisor.last_name,
                    'email': secondary_supervisor.email
                }
            except ObjectDoesNotExist:
                secondary_supervisor_data = {}

            # t_members = TeamMember.objects.filter(team_id=team.team_id)
            # members_data = []
            # for t_member in t_members:
            #     member_id = t_member.student_id
            #     member = Student.objects.get(student_id=member_id)
            #     member_data = {
            #         'id': member_id,
            #         'name': member.name,
            #         'email': member.email
            #     }
            #     members_data.append(member_data)

            team_data = {
                'id': team.team_id,
                'name': team.name,
                'project_name': team.project_name,
                # 'description': team.description,
                # 'subject_id': team.subject_id,
                # 'year': team.year,
                'supervisor': supervisor_data,
                'secondary_supervisor': secondary_supervisor_data,
                # 'create_date': team.create_date,
                # 'expired': team.expired,
                # 'member': members_data
            }
            teams.append(team_data)
    return teams


def multi_get_team(request):
    """
        Get multiple teams

        :param request: supervisor_id/coordinator_id
        :return:
        """
    account_id = request.GET.get('account_id', None)
    offset = int(request.POST.get('offset', 0))
    has_more = 0
    filtered_teams = []
    teams = []
    try:
        user = User.objects.get(account_id=account_id)
    except ObjectDoesNotExist:
        resp = init_http_response(RespCode.invalid_op.value.key, RespCode.invalid_op.value.msg)
        return make_json_response(HttpResponseBadRequest, resp)
    # coordinators
    if user.role == Roles.coordinator.value.key:
        subjects = Subject.objects.filter(coordinator_id=user.account_id)
        for subject in subjects:
            filtered_teams.append(Team.objects.filter(subject_id=subject.subject_code))
    # supervisors
    elif user.role == Roles.supervisor.value.key:
        filtered_teams.append(Team.objects.filter(supervisor_id=user.account_id))
        filtered_teams.append(Team.objects.filter(secondary_supervisor_id=user.account_id))
    # admins
    else:
        filtered_teams.append(Team.objects.all())
    teams.append(get_teams_data(filtered_teams))
    # TODO: paging
    # kwargs = dict()
    # if ids:
    #     kwargs['team_id__in'] = [int(x) for x in ids.split(',')]
    # if code:
    #     kwargs['subject_code__contains'] = code
    # if name:
    #     kwargs['name__contains'] = name
    #
    # teams = Team.objects.filter(teams).order_by('team_id')[offset: offset + SINGLE_PAGE_LIMIT + 1]
    #
    # if len(teams) > SINGLE_PAGE_LIMIT:
    #     teams = teams[: SINGLE_PAGE_LIMIT]
    #     has_more = 1
    # offset += len(teams)

    body = {
        'teams': teams
    }
    return HttpResponse(json.dumps(body), content_type="application/json")


"""
Assign supervisor or secondary supervisor for a specific team

Method: Post
Url: localhost:8000/api/v1/team/<team_id>
Params: team_id
Request: 
        {
            "supervisor_id":                    #supervisor_id
            "secondary_supervisor_id":          #secondary_supervisor_id
        }
"""


@check_body
def update_team(request, body, team_id: int):
    """
            Post secondary_supervisor_id

            :param request:
            :param team_id:
            :return:
            """
    supervisor_id = None
    secondary_supervisor_id = None

    if "supervisor_id" in body.keys():
        try:
            supervisor_id = body['supervisor_id']
            supervisor = User.objects.get(account_id=supervisor_id)
        except ObjectDoesNotExist:
            resp = init_http_response(RespCode.invalid_op.value.key, RespCode.invalid_op.value.msg)
            resp['supervisor'] = "Invalid supervisor_id"
            return HttpResponse(json.dumps(resp), content_type="application/json")
    # secondary_supervisor_id = request.POST.get('secondary_supervisor_id', None)
    if "secondary_supervisor_id" in body.keys():
        try:
            secondary_supervisor_id = body['secondary_supervisor_id']
            secondary_supervisor = User.objects.get(account_id=secondary_supervisor_id)
        except ObjectDoesNotExist:
            resp = init_http_response(RespCode.invalid_op.value.key, RespCode.invalid_op.value.msg)
            resp['secondary_supervisor'] = "Invalid secondary_supervisor_id"
            return HttpResponse(json.dumps(resp), content_type="application/json")
    try:
        team = Team.objects.get(team_id=team_id)
    except ObjectDoesNotExist:
        resp = init_http_response(RespCode.invalid_op.value.key, RespCode.invalid_op.value.msg)
        resp['team'] = "Invalid team_id"
        return make_json_response(HttpResponseBadRequest, resp)

    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    if supervisor_id and team.supervisor_id != supervisor_id:
        team.supervisor_id = supervisor_id
        if team.secondary_supervisor_id == supervisor_id:
            team.secondary_supervisor_id = None
        team.save()
        resp['supervisor'] = "Update successfully"

    if secondary_supervisor_id and team.secondary_supervisor_id != secondary_supervisor_id:
        team.secondary_supervisor_id = secondary_supervisor_id
        if team.supervisor_id == secondary_supervisor_id:
            team.supervisor_id = None
        team.save()
        resp['secondary_supervisor'] = "Update successfully"

    return HttpResponse(json.dumps(resp), content_type="application/json")


"""
Get all team members of a team

Method: Get
Url: localhost:8000/api/v1/team/<team_id>/members
Params: team_id
Request:
"""


@require_http_methods(['GET'])
@check_user_login
def get_team_members(request, *args, **kwargs):
    """
        Get certain team members

        :param request:
        :param team_id:
        :return:
        """

    team_id = None
    for arg in args:
        if isinstance(arg, dict):
            team_id = arg.get('team_id', None)
    # Queryset list of team members
    team_members = []
    # Result list for members: supervisor, secondary_supervisor, and team members
    members = []
    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    try:
        team = Team.objects.get(team_id=team_id)
        team_members.append(TeamMember.objects.filter(team_id=team_id))
    except ObjectDoesNotExist:
        return make_json_response(HttpResponseBadRequest, resp)
    try:
        supervisor = User.objects.get(account_id=team.supervisor_id)
        if supervisor:
            supervisor_data = {
                'supervisor_id': supervisor.account_id,
                'supervisor_first_name': supervisor.first_name,
                'supervisor_last_name': supervisor.last_name,
                'email': supervisor.email
            }
            members.append(supervisor_data)
    except ObjectDoesNotExist:
        resp['supervisor'] = "supervisor not exist"
    try:
        secondary_supervisor = User.objects.get(account_id=team.secondary_supervisor_id)
        if secondary_supervisor:
            secondary_supervisor_data = {
                'secondary_supervisor_id': secondary_supervisor.account_id,
                'secondary_supervisor_first_name': secondary_supervisor.first_name,
                'secondary_supervisor_last_name': secondary_supervisor.last_name,
                'email': secondary_supervisor.email,
            }
            members.append(secondary_supervisor_data)
    except ObjectDoesNotExist:
        resp['secondary_supervisor'] = "secondary_supervisor not exist"
    for member in team_members[0]:
        student = Student.objects.get(student_id=member.student_id)
        member_data = {
            'student_id': student.student_id,
            'fullname': student.first_name,
            'email': student.email
        }
        members.append(member_data)

    data = {
        'team_members': members
    }

    resp['data'] = data
    return make_json_response(HttpResponse, resp)