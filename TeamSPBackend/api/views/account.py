import logging
import requests

from django.http import HttpResponseNotAllowed, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, ObjectDoesNotExist
from django.db import transaction

from atlassian import Confluence
from TeamSPBackend.account.models import Account, User
from TeamSPBackend.common.config import SINGLE_PAGE_LIMIT
from TeamSPBackend.common.utils import make_json_response, check_user_login, body_extract, mills_timestamp, check_body, init_http_response_my_enum
from TeamSPBackend.common.choices import RespCode, Status, Roles, get_keys
from TeamSPBackend.api.dto.dto import LoginDTO, AddAccountDTO, UpdateAccountDTO

logger = logging.getLogger('django')


@require_http_methods(['POST', 'GET'])
@check_user_login()
def account_router(request, *args, **kwargs):
    if request.method == 'POST':
        return add_account(request)
    elif request.method == 'GET':
        return get_account(request)
    return HttpResponseNotAllowed(['POST'])


@require_http_methods(['GET'])
@check_user_login(get_keys([Roles.coordinator, Roles.admin]))
def supervisor_router(request, *args, **kwargs):
    supervisor_id = None
    if isinstance(kwargs, dict):
        supervisor_id = kwargs.get('id', None)
    if supervisor_id:
        return get_supervisor(request, supervisor_id, *args, **kwargs)
    return multi_get_supervisor(request, *args, **kwargs)


@require_http_methods(['POST'])
@check_body
def login(request, body, *args, **kwargs):
    """
    Login
    Method: Post
    Request: username(can input username or email to this), password
    """

    login_dto = LoginDTO()
    body_extract(body, login_dto)

    if not login_dto.validate():
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    login_dto.encrypt()
    account = None
    try:
        if login_dto.username:
            account = Account.objects.get(username=login_dto.username, password=login_dto.md5, status=Status.valid.key)
        elif login_dto.email:
            account = Account.objects.get(email=login_dto.email, password=login_dto.md5, status=Status.valid.key)
    except ObjectDoesNotExist:
        resp = init_http_response_my_enum(RespCode.login_fail)
        return make_json_response(resp=resp)

    user = User.objects.get(account_id=account.account_id)

    session_data = dict(
        id=user.user_id,
        name=user.get_name(),
        role=user.role,
        is_login=True,
        atl_login=False,
        atl_username=None,
        atl_password=None,
    )
    request.session['user'] = session_data

    data = dict(
        user_id=user.user_id,
        account_id=account.account_id,
        role=user.role,
        name=user.get_name()
    )
    resp = init_http_response_my_enum(RespCode.success, data)
    return make_json_response(resp=resp)


@require_http_methods(['POST'])
def logout(request, *args, **kwargs):
    """

    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    user = request.session.get('user')
    if user is None:
        resp = init_http_response_my_enum(RespCode.not_logged)
        return make_json_response(resp=resp)

    request.session.flush()
    resp = init_http_response_my_enum(RespCode.success)
    return make_json_response(resp=resp)


@check_body
def add_account(request, body, *args, **kwargs):
    """
    Create account and user
    Method: Post
    Request: username, email, password, role, first_name, last_name
    """

    add_account_dto = AddAccountDTO()
    body_extract(body, add_account_dto)

    if not add_account_dto.not_empty() or not add_account_dto.validate():
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    if Account.objects.filter(Q(username=add_account_dto.username) | Q(email=add_account_dto.email)).exists():
        resp = init_http_response_my_enum(RespCode.account_existed)
        return make_json_response(resp=resp)

    add_account_dto.encrypt()
    timestamp = mills_timestamp()

    try:
        with transaction.atomic():
            account = Account(username=add_account_dto.username, email=add_account_dto.email,
                              password=add_account_dto.md5, status=Status.valid.key, create_date=timestamp,
                              update_date=timestamp)
            account.save()

            user = User(account_id=account.account_id, username=add_account_dto.username,
                        first_name=add_account_dto.first_name, last_name=add_account_dto.last_name,
                        role=add_account_dto.role, status=Status.valid.key,
                        create_date=timestamp, update_date=timestamp, email=add_account_dto.email)
            user.save()
    except Exception as e:
        print(e)
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    resp = init_http_response_my_enum(RespCode.success)
    return make_json_response(resp=resp)


def get_account(request):
    """
    Get Account
    Method: Get
    Request: accountId
    """
    user = request.session.get('user')
    user_id = user['id']

    try:
        user = User.objects.get(user_id=user_id, status=Status.valid.key)
    except ObjectDoesNotExist:
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    account_id = int(request.GET.get('id', user.account_id))
    if not account_id:
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    try:
        account = Account.objects.get(account_id=account_id, status=Status.valid.key)
    except ObjectDoesNotExist:
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    data = dict(
        username=account.username,
        email=account.email,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    resp = init_http_response_my_enum(RespCode.success, data)
    return make_json_response(resp=resp)


@require_http_methods(['POST'])
@check_user_login()
@check_body
def atl_login(request, body, *args, **kwargs):
    """
    Update atlassian login info
    Method: Post
    Request: first_name,last_name,old_password,password
    """
    try:
        user = request.session.get('user', {})
        # if user['atl_login']:
        #     resp = init_http_response_my_enum(RespCode.success)
        #     return make_json_response(resp=resp)

        user['atl_username'] = body['atl_username']
        user['atl_password'] = body['atl_password']
        # user['atl_login'] = True
        request.session['user'] = user

        confluence = Confluence(
            url='https://confluence.cis.unimelb.edu.au:8443/',
            username=request.session['user']['atl_username'],
            password=request.session['user']['atl_password']
        )

        conf_resp = confluence.get_all_groups()

        # print("~~")
        # print(request.session['user']['atl_username'])
        resp = init_http_response_my_enum(RespCode.success)
        return make_json_response(resp=resp)
    except requests.exceptions.HTTPError as e:
        resp = init_http_response_my_enum(RespCode.server_error)
        return make_json_response(resp=resp)


@require_http_methods(['POST'])
@check_user_login()
@check_body
def update_account(request, body, *args, **kwargs):
    """
    Update account
    Method: Post
    Request: first_name,last_name,old_password,password
    """
    user = request.session.get('user')
    user_id = user['id']

    update_account_dto = UpdateAccountDTO()
    body_extract(body, update_account_dto)
    update_account_dto.encrypt()

    try:
        user = User.objects.get(user_id=user_id, status=Status.valid.key)
        account = Account.objects.get(account_id=user.account_id, status=Status.valid.key)
    except ObjectDoesNotExist:
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    if (update_account_dto.old_password and update_account_dto.old_md5 != account.password) \
            or not update_account_dto.validate():
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    timestamp = mills_timestamp()
    if update_account_dto.first_name:
        user.first_name = update_account_dto.first_name
        user.update_date = timestamp
    if update_account_dto.role:
        user.role = update_account_dto.role
        user.update_date = timestamp
    if update_account_dto.last_name:
        user.last_name = update_account_dto.last_name
        user.update_date = timestamp
    if update_account_dto.atl_username:
        user.atl_username = update_account_dto.atl_username
        user.update_date = timestamp
    if update_account_dto.atl_password:
        update_account_dto.encrypt_aes()
        user.atl_password = update_account_dto.aes
        user.update_date = timestamp
    if update_account_dto.old_password and update_account_dto.password \
            and update_account_dto.old_md5 == account.password:
        account.password = update_account_dto.md5
        account.update_date = timestamp

    try:
        with transaction.atomic():
            user.save()
            account.save()
    except Exception as e:
        print(e)
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    resp = init_http_response_my_enum(RespCode.success)
    return make_json_response(resp=resp)


@require_http_methods(['POST'])
@check_user_login(get_keys([Roles.coordinator, Roles.admin]))
@check_body
def delete(request, body, *args, **kwargs):
    """
    Delete Account
    Method: Post
    Request: accountId
    """
    account_id = body.get('id')

    try:
        account = Account.objects.get(account_id=account_id, status=Status.valid.key)
        user = User.objects.get(account_id=account_id, status=Status.valid.key)
    except ObjectDoesNotExist:
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    timestamp = mills_timestamp()

    try:
        with transaction.atomic():
            account.status = Status.invalid.key
            account.update_date = timestamp
            account.save()
            user.status = Status.invalid.key
            user.update_date = timestamp
            user.save()
    except Exception as e:
        print(e)
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    resp = init_http_response_my_enum(RespCode.success)
    return make_json_response(resp=resp)


def get_supervisor(request, supervisor_id, *args, **kwargs):
    """

    :param request:
    :param supervisor_id:
    :param args:
    :param kwargs:
    :return:
    """

    try:
        supervisor = User.objects.get(user_id=supervisor_id, role=Roles.supervisor.key, status=Status.valid.key)
    except ObjectDoesNotExist as e:
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    data = dict(
        id=supervisor.user_id,
        name=supervisor.get_name(),
        email=supervisor.email,
    )
    resp = init_http_response_my_enum(RespCode.success, data)
    return make_json_response(resp=resp)


def multi_get_supervisor(request, *args, **kwargs):
    """

    :param request:
    :param args:
    :param kwargs:
    :return:
    """

    offset = int(request.GET.get('offset', 0))
    has_more = 0

    supervisors = User.objects.filter(role=Roles.supervisor.key, status=Status.valid.key)\
        .only('user_id')[offset: offset + SINGLE_PAGE_LIMIT + 1]
    if len(supervisors) > SINGLE_PAGE_LIMIT:
        supervisors = supervisors[: SINGLE_PAGE_LIMIT]
        has_more = 1
    offset += len(supervisors)

    data = dict(
        supervisors=[supervisor.user_id for supervisor in supervisors],
        offset=offset,
        has_more=has_more,
    )
    resp = init_http_response_my_enum(RespCode.success, data)
    return make_json_response(resp=resp)
