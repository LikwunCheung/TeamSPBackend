# -*- coding: utf-8 -*-

import ujson

from django.http.response import HttpResponseForbidden, HttpResponseBadRequest, HttpResponse, HttpResponseRedirect

from TeamSPBackend.common.config import ErrorCode, ErrorMsg


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


def init_http_success(err_msg=None):
    if not err_msg:
        return init_http_response(ErrorCode.success.value, ErrorMsg.success.value)
    return init_http_response(ErrorCode.success.value, err_msg)
