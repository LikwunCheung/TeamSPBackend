# -*- coding: utf-8 -*-

import ujson
import time

from django.http.response import HttpResponseForbidden, HttpResponseBadRequest, HttpResponse, HttpResponseRedirect

from TeamSPBackend.common.choices import RespCode
from TeamSPBackend.common.config import SESSION_REFRESH


def make_json_response(func=HttpResponse, resp=None):
    return func(ujson.dumps(resp), content_type='application/json')


def make_redirect_response(func=HttpResponse, resp=None):
    return func(ujson.dumps(resp), content_type='application/json', status=302)


def init_http_response(err_code, err_msg):
    return dict(
        err_code=err_code,
        err_msg=err_msg,
        data=dict(),
    )


def check_user_login(func):
    """
    Disable for testing
    :param func:
    :return:
    """
    def wrapper(request, *args, **kwargs):
        user = request.session.get('user', {})
        if not user or 'id' not in user or 'is_login' not in user:
            resp = init_http_response(RespCode.not_logged.value.key, RespCode.not_logged.value.msg)
            return make_json_response(HttpResponseBadRequest, resp)

        request.session.set_expiry(SESSION_REFRESH)
        return func(request, args, kwargs)
    return wrapper


def check_user_role(func, role):
    """
    Disable for testing
    :param func:
    :return:
    """
    def wrapper(request, *args, **kwargs):
        user = request.session.get('user', {})
        user_role = user['role']
        if user_role is not role:
            resp = init_http_response(RespCode.permission_deny.value.key, RespCode.permission_deny.value.msg)
            return make_json_response(HttpResponseBadRequest, resp)

        return func(request, args, kwargs)
    return wrapper


def body_extract(body: dict, obj: object):
    """

    :param body:
    :param obj:
    :return:
    """
    for i in obj.__dict__.keys():
        if i in body:
            obj.__setattr__(i, body.get(i))


def mills_timestamp():
    return int(time.time() * 1000)
