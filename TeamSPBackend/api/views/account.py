import json

from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.utils.timezone import now
from django.db.models import Q

from TeamSPBackend.account.models import Account, User
from TeamSPBackend.common.utils import init_http_response, make_json_response, check_user_login
from TeamSPBackend.common.choices import RespCode, Status, Roles


@require_http_methods(['POST', 'GET'])
@check_user_login
def account_router(request, *args, **kwargs):
    if request.method == 'POST':
        return add_account(request)
    elif request.method == 'GET':
        return get_account(request)
    return HttpResponseNotAllowed(['POST'])


@require_http_methods(['POST'])
def login(request):
    """
    Login
    Method: Post
    Request: username(can input username or email to this), password
    """

    username = request.POST.get('username', '')
    email = request.POST.get('email', '')
    if not username and not email:
        resp = init_http_response(RespCode.invalid_parameter, RespCode.RespCodeChoice.invalid_parameter)
        return make_json_response(HttpResponseBadRequest, resp)

    password = request.POST.get('password', '')

    account = None
    if username:
        account = Account.objects.get(username=username, password=password, status=Status.valid)
    elif email:
        account = Account.objects.get(email=email, password=password, status=Status.valid)

    if not account or not password:
        resp = init_http_response(RespCode.login_fail, RespCode.RespCodeChoice.login_fail)
        return make_json_response(HttpResponseBadRequest, resp)

    user = User.objects.get(account_id=account.account_id)

    session_data = dict(
        id=user.user_id,
        role=user.role,
        is_login=True,
    )
    request.session['user'] = session_data

    data = dict(
        user_d=user.user_id,
        account_id=account.id,
        role=user.role,
        name=user.get_name()
    )
    resp = init_http_response(RespCode.success, RespCode.RespCodeChoice.success)
    resp['data'] = data
    return make_json_response(HttpResponse, resp)


def add_account(request):
    """
    Create account and user
    Method: Post
    Request: username, email, password, role, first_name, last_name
    """
    username = request.POST.get('username', '')
    email = request.POST.get('email', '')
    password = request.POST.get('password', '')
    role = request.POST.get('role', '')
    first_name = request.POST.get('first_name', '')
    last_name = request.POST.get('last_name', '')

    if not username or not email or not password or not role or not first_name or not last_name:
        resp = init_http_response(RespCode.invalid_parameter, RespCode.RespCodeChoice.invalid_parameter)
        return make_json_response(HttpResponseBadRequest, resp)

    if Account.objects.filter(Q(username=username) | Q(email=email)).exists():
        resp = init_http_response(RespCode.account_existed, RespCode.RespCodeChoice.account_existed)
        return make_json_response(HttpResponseBadRequest, resp)

    timestamp = int(now().timestamp())
    account = Account(username=username, email=email, password=password, status=Status.valid, create_date=timestamp,
                      update_date=timestamp)
    account.save()

    user = User(account_id=account.id, username=username, first_name=first_name, last_name=last_name, role=role,
                status=Status.valid, create_date=timestamp, update_date=timestamp, email=email)
    user.save()

    resp = init_http_response(RespCode.success, RespCode.RespCodeChoice.success)
    return make_json_response(HttpResponse, resp)


def get_account(request):
    """
    Get Account
    Method: Get
    Request: accountId
    """
    user = request.session.get('user')
    account_id = user['account_id']
    account_id = int(request.GET.get('id', account_id))

    if not account_id:
        resp = init_http_response(RespCode.invalid_parameter, RespCode.RespCodeChoice.invalid_parameter)
        return make_json_response(HttpResponseBadRequest, resp)

    account = Account.objects.get(account_id=account_id, status=Status.valid)
    user = User.objects.get(account_id=account_id, status=Status.valid)
    if not account or not user:
        resp = init_http_response(RespCode.invalid_parameter, RespCode.RespCodeChoice.invalid_parameter)
        return make_json_response(HttpResponseBadRequest, resp)

    data = dict(
        username=account.username,
        email=account.email,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    resp = init_http_response(RespCode.success, RespCode.RespCodeChoice.success)
    resp['data'] = data
    return make_json_response(HttpResponse, resp)


@require_http_methods(['POST'])
@check_user_login
def update_account(request, *args, **kwargs):
    """
    Update account
    Method: Post
    Request: first_name,last_name,old_password,password
    """
    user = request.session.get('user')
    user_id = user['user_id']
    account_id = user['account_id']

    first_name = request.POST.get('first_name', '')
    last_name = request.POST.get('last_name', '')
    old_psw = request.POST.get('old_password', '')
    new_psw = request.POST.get('password', '')

    user = User.objects.get(user_id=user_id, status=Status.valid)
    account = Account.objects.get(account_id=account_id, status=Status.valid)

    if not user or not account:
        resp = init_http_response(RespCode.invalid_parameter, RespCode.RespCodeChoice.invalid_parameter)
        return make_json_response(HttpResponseBadRequest, resp)

    if old_psw and old_psw != account.password:
        resp = init_http_response(RespCode.invalid_parameter, RespCode.RespCodeChoice.invalid_parameter)
        return make_json_response(HttpResponseBadRequest, resp)

    timestamp = int(now().timestamp())
    if first_name:
        user.first_name = first_name
        user.update_date = timestamp
    if last_name:
        user.last_name = last_name
        user.update_date = timestamp
    if old_psw and new_psw and old_psw == account.password:
        account.password = new_psw
        account.update_date = timestamp

    user.save()
    account.save()
    resp = init_http_response(RespCode.success, RespCode.RespCodeChoice.success)
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
    if role is not Roles.admin:
        resp = init_http_response(RespCode.invalid_op, RespCode.RespCodeChoice.invalid_op)
        return make_json_response(HttpResponseBadRequest, resp)

    account_id = request.POST.get('id')
    account = Account.objects.get(account_id=account_id, status=Status.valid)
    user = User.objects.get(account_id=account_id, status=Status.valid)

    if not account and not user:
        resp = init_http_response(RespCode.invalid_parameter, RespCode.RespCodeChoice.invalid_parameter)
        return make_json_response(HttpResponseBadRequest, resp)

    timestamp = int(now().timestamp())
    account.status = Status.invalid
    account.update_date = timestamp
    account.save()
    user.status = Status.invalid
    user.update_date = timestamp
    user.save()

    resp = init_http_response(RespCode.success, RespCode.RespCodeChoice.success)
    return make_json_response(HttpResponse, resp)


"""
Accept Invitation and Create Account (WIP)
Method: Post
Request: key, username, password
"""


def invite_accept(request):
    if request.method == 'POST':

        key = request.POST.get('key')
        username = request.POST.get('username')
        password = request.POST.get('password')
        if Account.objects.filter(username=username).exists():
            resp = {'code': -1, 'msg': 'username already exist'}
            return HttpResponse(json.dumps(resp), content_type="application/json")
        else:
            account = Account(username=username, password=password, status=1)
            user = User(username=username, status=1)
            account.save()
            user.save()
            resp = {'code': 0, 'msg': 'invite accept'}
            return HttpResponse(json.dumps(resp), content_type="application/json")
