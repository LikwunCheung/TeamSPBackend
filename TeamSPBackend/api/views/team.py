import json
from django.http.response import HttpResponseBadRequest
from django.http import HttpResponse, HttpResponseNotAllowed
from django.utils.timezone import now
from django.views.decorators.http import require_http_methods
from TeamSPBackend.common.utils import check_user_login, make_json_response, init_http_response
from TeamSPBackend.common.choices import RespCode, Roles
from TeamSPBackend.account.models import Account
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
        # Create team from request with supervisor_id
        return create_team(request)  # todo: might need to change for retrieving confluence data / front-end request with team info
    elif request.method == 'GET':
        if team_id:
            # Get a specific team information
            return get_team_members(request, team_id)  # done
        # Get teams information
        return multi_get_team(request)  # done
    return HttpResponseNotAllowed(['POST'])


"""
Create team from csv (not used anymore)
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
        duration = request.POST.get('duration')
        timestamp = int(now().timestamp())
        expired = timestamp + 60 * 60 * 24 * int(duration)
        team = Team(name=name, description=description, supervisor_id=supervisor_id,
                    year=year, create_date=timestamp, expired=expired)
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
    for team in filtered_teams:
        supervisor = Account.objects.get(account_id=team.supervisor_id)
        supervisor_data = {
            'supervisor_id': supervisor.account_id,
            'first_name': supervisor.first_name,
            'last_name': supervisor.last_name,
            'email': supervisor.email
        }

        secondary_supervisor = Account.objects.get(account_id=team.secondary_supervisor_id)
        secondary_supervisor_data = {
            'secondary_supervisor_id': secondary_supervisor.account_id,
            'first_name': secondary_supervisor.first_name,
            'last_name': secondary_supervisor.last_name,
            'email': secondary_supervisor.email
        }

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

        :param request: supervisor_id (necessary), subject_id or year (optional)||team_ids (optional)
        :return:
        """
    supervisor_id = request.get('supervisor_id', None)
    filtered_teams = []
    teams = []
    try:
        user = User.objects.get(user_id=supervisor_id)
    except ObjectDoesNotExist:
        resp = init_http_response(RespCode.invalid_op.value.key, RespCode.invalid_op.value.msg)
        return make_json_response(HttpResponseBadRequest, resp)
    # coordinators
    if user.role == Roles.coordinator.value.key:
        subject_ids = Subject.objects.filter(coordinator_id=user.user_id)
        for subject_id in subject_ids:
            filtered_teams.append(Team.objects.filter(subject_id=subject_id))
    # supervisors
    elif user.role == Roles.supervisor.value.key:
        filtered_teams.append(Team.objects.filter(supervisor_id=user.user_id))
        filtered_teams.append(Team.objects.filter(secondary_supervisor_id=user.id))
    # admins
    else:
        filtered_teams. append(Team.objects)
    teams.append(get_teams_data(filtered_teams))
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


def update_team(request, team_id: int):
    """
            Post secondary_supervisor_id

            :param request:
            :param team_id:
            :return:
            """
    supervisor_id = request.GET('supervisor_id', None)
    secondary_supervisor_id = request.GET('secondary_supervisor_id', None)
    try:
        team = Team.objects.get(team_id=team_id)
    except ObjectDoesNotExist:
        resp = init_http_response(RespCode.invalid_op.value.key, RespCode.invalid_op.value.msg)
        return make_json_response(HttpResponseBadRequest, resp)
    if supervisor_id and team.supervisor_id != supervisor_id:
        team.supervisor_id = supervisor_id
        team.save()
        resp = {'code': 0, 'msg': 'Update successfully'}
    if secondary_supervisor_id and team.secondary_supervisor_id != secondary_supervisor_id:
        team.secondary_supervisor_id = secondary_supervisor_id
        team.save()
        resp = {'code': 0, 'msg': 'Update successfully'}
    if resp:
        return HttpResponse(json.dumps(resp), content_type="application/json")
    else:
        resp = {'code': -1, 'msg': 'Nothing to update'}
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
def get_team_members(request, *args):
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
    try:
        team = Team.objects.get(team_id=team_id)
        team_members = TeamMember.objects.get(team_id=team_id)
    except ObjectDoesNotExist:
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponseBadRequest, resp)

    supervisor = User.objects.get(user_id=team.supervisor_id)
    secondary_supervisor = User.objects.get(user_id=team.secondary_supervisor_id)

    members = []

    if supervisor:
        supervisor_data = {
            'supervisor_id', supervisor.user_id,
            'supervisor_first_name', supervisor.first_name,
            'supervisor_last_name', supervisor.last_name,
            'email', supervisor.email
        }
        members.append(supervisor_data)

    if secondary_supervisor:
        secondary_supervisor_data = {
            'secondary_supervisor_id', secondary_supervisor.user_id,
            'secondary_supervisor_first_name', secondary_supervisor.first_name,
            'secondary_supervisor_last_name', secondary_supervisor.last_name,
            'email', secondary_supervisor.email,

        }
        members.append(secondary_supervisor_data)

    for member in team_members:
        student = Student.objects.get(id=member.student_id)
        member_data = {
            'student_id': student.student_id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'email': student.email
        }
        members.append(member_data)

    data = {
        'team_members': members
    }

    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    resp['data'] = data
    return make_json_response(HttpResponse, resp)
