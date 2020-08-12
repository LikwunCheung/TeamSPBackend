import ujson

from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, ObjectDoesNotExist
from django.db import transaction

from TeamSPBackend.account.models import Account, User
from TeamSPBackend.common.utils import init_http_response, make_json_response, check_user_login, body_extract, mills_timestamp, check_body
from TeamSPBackend.common.choices import RespCode, Status, Roles
from TeamSPBackend.api.dto.dto import LoginDTO, AddAccountDTO, UpdateAccountDTO


@require_http_methods(['POST', 'GET'])
@check_user_login
def account_router(request, *args, **kwargs):
    if request.method == 'POST':
        return add_account(request)
    elif request.method == 'GET':
        return get_account(request)
    return HttpResponseNotAllowed(['POST'])


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
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponse, resp)

    login_dto.encrypt()
    account = None
    try:
        if login_dto.username:
            account = Account.objects.get(username=login_dto.username, password=login_dto.md5, status=Status.valid.value.key)
        elif login_dto.email:
            account = Account.objects.get(email=login_dto.email, password=login_dto.md5, status=Status.valid.value.key)
    except ObjectDoesNotExist:
        resp = init_http_response(RespCode.login_fail.value.key, RespCode.login_fail.value.msg)
        return make_json_response(HttpResponse, resp)

    user = User.objects.get(account_id=account.account_id)

    session_data = dict(
        id=user.user_id,
        role=user.role,
        is_login=True,
    )
    request.session['user'] = session_data

    data = dict(
        user_id=user.user_id,
        account_id=account.account_id,
        role=user.role,
        name=user.get_name()
    )
    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    resp['data'] = data
    return make_json_response(HttpResponse, resp)


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
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponse, resp)

    if Account.objects.filter(Q(username=add_account_dto.username) | Q(email=add_account_dto.email)).exists():
        resp = init_http_response(RespCode.account_existed.value.key, RespCode.account_existed.value.msg)
        return make_json_response(HttpResponse, resp)

    add_account_dto.encrypt()
    timestamp = mills_timestamp()

    try:
        with transaction.atomic():
            account = Account(username=add_account_dto.username, email=add_account_dto.email,
                              password=add_account_dto.md5, status=Status.valid.value.key, create_date=timestamp,
                              update_date=timestamp)
            account.save()

            user = User(account_id=account.account_id, username=add_account_dto.username,
                        first_name=add_account_dto.first_name, last_name=add_account_dto.last_name,
                        role=add_account_dto.role, status=Status.valid.value.key,
                        create_date=timestamp, update_date=timestamp, email=add_account_dto.email)
            user.save()
    except Exception as e:
        print(e)
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponse, resp)

    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    return make_json_response(HttpResponse, resp)


def get_account(request):
    """
    Get Account
    Method: Get
    Request: accountId
    """
    user = request.session.get('user')
    user_id = user['id']

    try:
        user = User.objects.get(user_id=user_id, status=Status.valid.value.key)
    except ObjectDoesNotExist:
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponse, resp)

    account_id = int(request.GET.get('id', user.account_id))
    if not account_id:
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponse, resp)

    try:
        account = Account.objects.get(account_id=account_id, status=Status.valid.value.key)
    except ObjectDoesNotExist:
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponse, resp)

    data = dict(
        username=account.username,
        email=account.email,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    resp['data'] = data
    return make_json_response(HttpResponse, resp)


@require_http_methods(['POST'])
@check_user_login
@check_body
def update_account(request, body, *args, **kwargs):
    """
    Update account
    Method: Post
    Request: first_name,last_name,old_password,password
    """
    user = request.session.get('user')
    user_id = user['id']

    # body = dict(json.loads(request.body))
    update_account_dto = UpdateAccountDTO()
    body_extract(body, update_account_dto)
    update_account_dto.encrypt()

    try:
        user = User.objects.get(user_id=user_id, status=Status.valid.value.key)
        account = Account.objects.get(account_id=user.account_id, status=Status.valid.value.key)
    except ObjectDoesNotExist:
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponse, resp)

    if (update_account_dto.old_password and update_account_dto.old_md5 != account.password) \
            or not update_account_dto.validate():
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponse, resp)

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
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponse, resp)

    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    return make_json_response(HttpResponse, resp)


@require_http_methods(['POST'])
@check_user_login
def delete(request):
    """
    Delete Account
    Method: Post
    Request: accountId
    """

    user = request.session.get('user')
    role = user['role']

    if role is not Roles.admin.value.key:
        resp = init_http_response(RespCode.invalid_op.value.key, RespCode.invalid_op.value.msg)
        return make_json_response(HttpResponse, resp)

    account_id = request.POST.get('id')
    try:
        account = Account.objects.get(account_id=account_id, status=Status.valid.value.key)
        user = User.objects.get(account_id=account_id, status=Status.valid.value.key)
    except ObjectDoesNotExist:
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponse, resp)

    timestamp = mills_timestamp()

    try:
        with transaction.atomic():
            account.status = Status.invalid.value.key
            account.update_date = timestamp
            account.save()
            user.status = Status.invalid.value.key
            user.update_date = timestamp
            user.save()
    except Exception as e:
        print(e)
        resp = init_http_response(RespCode.invalid_parameter.value.key, RespCode.invalid_parameter.value.msg)
        return make_json_response(HttpResponse, resp)

    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    return make_json_response(HttpResponse, resp)


@require_http_methods(['POST'])
@check_user_login
def invite_accept(request):
    """
    Accept Invitation and Create Account (WIP)
    Method: Post
    Request: key, username, password
    """

    if request.method == 'POST':

        key = request.POST.get('key')
        username = request.POST.get('username')
        password = request.POST.get('password')

        timestamp = mills_timestamp()
        if Account.objects.filter(username=username).exists():
            resp = {'code': -1, 'msg': 'username already exist'}
            return HttpResponse(json.dumps(resp), content_type="application/json")
        else:
            account = Account(username=username, password=password, status=1, create_date=timestamp,)
            user = User(username=username, status=1, create_date=timestamp,)

            account.save()
            user.save()
            resp = {'code': 0, 'msg': 'invite accept'}
            return HttpResponse(json.dumps(resp), content_type="application/json")
