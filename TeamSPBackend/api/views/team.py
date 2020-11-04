import ujson
import logging

from django.http import HttpResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.db.models import Q, ObjectDoesNotExist

from TeamSPBackend.api.dto.dto import AddTeamDTO, UpdateTeamDTO

from TeamSPBackend.common.config import SINGLE_PAGE_LIMIT
from TeamSPBackend.common.utils import check_user_login, make_json_response, init_http_response, check_body, body_extract, mills_timestamp, init_http_response_my_enum
from TeamSPBackend.common.choices import RespCode, Roles, get_keys
from TeamSPBackend.account.models import Account
from TeamSPBackend.api.views.confluence.confluence import get_members
from TeamSPBackend.team.models import Team, Student, TeamMember
from TeamSPBackend.subject.models import Subject
from TeamSPBackend.account.models import User

logger = logging.getLogger('django')


@require_http_methods(['POST', 'GET'])
#  @check_user_login()
def team_router(request, *args, **kwargs):
    team_id = None
    if isinstance(kwargs, dict):
        team_id = kwargs.get('id', None)
    if request.method == 'POST':
        if team_id:
            # Assign secondary supervisor for a specific team
            return update_team(request, team_id, *args, **kwargs)  # done
        # Import team from confluence with supervisor_id
        return import_team(request, *args, **kwargs)
        # Todo: might need to change for retrieving confluence data / front-end request with team info
    elif request.method == 'GET':
        if team_id:
            # Get a specific team information
            return get_team_members(request, team_id, *args, **kwargs)  # done
        # Get teams information
        return multi_get_team(request, *args, **kwargs)  # done
    return HttpResponseNotAllowed(['POST', 'GET'])


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


# @check_user_login(get_keys([Roles.admin, Roles.coordinator]))
@check_body
def import_team(request, body, *args, **kwargs):
    """
    Import team from confluence with supervisor_id
    :param request:
    :param body:
    :param args:
    :param kwargs:
    :return:
    """

    add_team_dto = AddTeamDTO()
    body_extract(body, add_team_dto)

    # Check parameters
    if not add_team_dto.not_empty():
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponse, resp)

    team_members = get_members(request, add_team_dto.team)
    if not team_members:
        logger.info('Empty team member: %s', add_team_dto.team)
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponse, resp)

    # If the team existed
    if Team.objects.filter(name=add_team_dto.team).exists():
        resp = init_http_response(RespCode.team_existed.value.key, RespCode.team_existed.value.msg)
        return make_json_response(HttpResponse, resp)

    try:
        with transaction.atomic():
            team = Team(name=add_team_dto.team, subject_code=add_team_dto.subject, year=add_team_dto.year,
                        project_name=add_team_dto.project, create_date=mills_timestamp())
            team.save()

            for member in team_members:
                try:
                    student = Student.objects.get(email=member['email'])
                except ObjectDoesNotExist as e:
                    student = Student(fullname=member['name'], email=member['email'])
                    student.save()
                import_team_member(team.team_id, student.student_id)

    except Exception as e:
        logger.error(e)
        resp = init_http_response(RespCode.server_error.value.key, RespCode.server_error.value.msg)
        return make_json_response(HttpResponse, resp)

    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    return make_json_response(HttpResponse, resp)


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

#
# def create_team(request):
#     try:
#         name = request.POST.get('name')
#         description = request.POST.get('description')
#         # supervisor = Account.objects.get(username = request.POST.get('supervisor'))
#         supervisor_id = request.POST.get('supervisor_id')
#         year = request.POST.get('year')
#         # member_id = request.POST.get('member_id')
#         # duration = request.POST.get('duration')
#         project_name = request.POST.get('project_name')
#         timestamp = int(now().timestamp())
#         # expired = timestamp + 60 * 60 * 24 * int(duration)
#         team = Team(name=name, description=description, supervisor_id=supervisor_id,
#                     year=year, create_date=timestamp, project_name=project_name)
#         team.save()
#         resp = {'code': 0, 'msg': 'create successfully'}
#         return HttpResponse(json.dumps(resp), content_type="application/json")
#     except ObjectDoesNotExist:
#         resp = {'code': -1, 'msg': 'error'}
#         return HttpResponse(json.dumps(resp), content_type="application/json")


"""
Create relation between team and members
Method: Post
Request: team_id, student_id
"""

#
# def team_member(request):
#     try:
#         student_id = request.POST.get('student_id')
#         team_id = request.POST.get('team_id')
#         if TeamMember.objects.filter(team_id=team_id, student_id=student_id).exists():
#             resp = {'code': 0, 'msg': 'exist'}
#             return HttpResponse(json.dumps(resp), content_type="application/json")
#         else:
#             TeamMember(student_id=student_id, team_id=team_id).save()
#             resp = {'code': 1, 'msg': 'add student to team'}
#             return HttpResponse(json.dumps(resp), content_type="application/json")
#     except:
#         resp = {'code': -1, 'msg': 'error'}
#         return HttpResponse(json.dumps(resp), content_type="application/json")
#

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
                'supervisor': supervisor_data,
                'secondary_supervisor': secondary_supervisor_data
            }
            teams.append(team_data)
    return teams


def multi_get_team(request, *args, **kwargs):
    """
    Get multiple teams
    :param request: supervisor_id/coordinator_id
    :return:
    """

    user = request.session.get('user', {})
    user_id = user['id']
    user_role = user['role']

    offset = int(request.POST.get('offset', 0))
    has_more = 0

    teams = list()
    if user_role == Roles.coordinator.value.key:
        subjects = Subject.objects.filter(coordinator_id=user_id)
        subject_codes = [subject.subject_code for subject in subjects]
        teams = Team.objects.filter(subject_code__in=subject_codes)

    elif user_role == Roles.supervisor.value.key:
        teams = Team.objects.filter(Q(supervisor_id=user_id) | Q(secondary_supervisor_id=user_id))

    elif user_role == Roles.admin.value.key:
        teams = Team.objects.all()

    teams = teams[offset: offset + SINGLE_PAGE_LIMIT + 1]
    if len(teams) > SINGLE_PAGE_LIMIT:
        teams = teams[: SINGLE_PAGE_LIMIT]
        has_more = 1
    offset += len(teams)

    supervisor_ids = list()
    supervisors = dict()
    for team in teams:
        if team.supervisor_id is not None:
            supervisor_ids.append(team.supervisor_id)
        if team.secondary_supervisor_id is not None:
            supervisor_ids.append(team.secondary_supervisor_id)

    if len(supervisor_ids) > 0:
        supervisors_temp = User.objects.filter(user_id__in=supervisor_ids)
        for supervisor in supervisors_temp:
            supervisors[supervisor.user_id] = supervisor

    data = dict(
        teams=[dict(
            id=team.team_id,
            name=team.name,
            project_name=team.project_name,
            year=team.year,
            supervisor=dict(
                id=supervisors[team.supervisor_id].user_id,
                name=supervisors[team.supervisor_id].get_name(),
                email=supervisors[team.supervisor_id].email
            ) if team.supervisor_id in supervisors else None,
            secondary_supervisor=dict(
                id=supervisors[team.secondary_supervisor_id].user_id,
                name=supervisors[team.secondary_supervisor_id].get_name(),
                email=supervisors[team.secondary_supervisor_id].email
            ) if team.secondary_supervisor_id in supervisors else None,
        ) for team in teams],
        offset=offset,
        has_more=has_more,
    )

    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    resp['data'] = data
    return make_json_response(HttpResponse, resp)


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
def update_team(request, body, *args, **kwargs):

    team_id = kwargs.get('id')
    update_team_dto = UpdateTeamDTO()
    body_extract(body, update_team_dto)

    try:
        team = Team.objects.get(team_id=team_id)
    except ObjectDoesNotExist as e:
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    if update_team_dto.supervisor_id:
        team.supervisor_id = update_team_dto.supervisor_id
    if update_team_dto.secondary_supervisor_id:
        team.secondary_supervisor_id = update_team_dto.secondary_supervisor_id

    team.save()
    resp = init_http_response_my_enum(RespCode.success)
    return make_json_response(resp=resp)


"""
Get all team members of a team
Method: Get
Url: localhost:8000/api/v1/team/<team_id>/members
Params: team_id
Request:
"""


@require_http_methods(['GET'])
#  @check_user_login()
def get_team_members(request, *args, **kwargs):
    """
        Get certain team members
        :param request:
        :param team_id:
        :return:
        """

    team_id = int(kwargs['id'])
    members = []
    data = dict()
    try:
        team = Team.objects.get(team_id=team_id)
        team_members = TeamMember.objects.filter(team_id=team_id)
    except ObjectDoesNotExist as e:
        logger.info(e)
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    try:
        supervisor = User.objects.get(account_id=team.supervisor_id)
        if supervisor:
            data['supervisor'] = supervisor_data = {
                'supervisor_id': supervisor.account_id,
                'supervisor_first_name': supervisor.first_name,
                'supervisor_last_name': supervisor.last_name,
                'email': supervisor.email
            }
    except ObjectDoesNotExist:
        data['supervisor'] = "supervisor not exist"

    try:
        secondary_supervisor = User.objects.get(account_id=team.secondary_supervisor_id)
        if secondary_supervisor:
            data['secondary_supervisor'] = secondary_supervisor_data = {
                'secondary_supervisor_id': secondary_supervisor.account_id,
                'secondary_supervisor_first_name': secondary_supervisor.first_name,
                'secondary_supervisor_last_name': secondary_supervisor.last_name,
                'email': secondary_supervisor.email,
            }
    except ObjectDoesNotExist:
        data['secondary_supervisor'] = "secondary_supervisor not exist"

    for member in team_members:
        student = Student.objects.get(student_id=member.student_id)
        member_data = {
            'student_id': student.student_id,
            'fullname': student.fullname,
            'email': student.email
        }
        members.append(member_data)

    data['team_members'] = members
    resp = init_http_response_my_enum(RespCode.success, data)
    return make_json_response(HttpResponse, resp)

