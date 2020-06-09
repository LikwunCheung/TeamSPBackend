# -*- coding: utf-8 -*-

import ujson

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
    def wrapper(request, *args, **kwargs):
        user = request.session.get('user', {})
        if not user or 'user_id' not in user or 'is_login' not in user:
            resp = init_http_response(RespCode.not_logged, RespCode.RespCodeChoice.not_logged)
            return make_json_response(HttpResponseBadRequest, resp)

        request.session.set_expiry(SESSION_REFRESH)
        return func(request, args, kwargs)
    return wrapper
