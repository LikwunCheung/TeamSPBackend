import datetime
import json
import random

from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.hashers import check_password
from django.utils.timezone import now

from TeamSPBackend.account.models import Account, User

"""
Account APIs
url: api/v1/account/...
"""




"""
Login
Method: Post
Request: username(can input username or email to this), password
"""
def login(request):

    if request.method == 'POST':
        name_email = request.POST.get('username')
        password = request.POST.get('password')
        if Account.objects.filter(username=name_email).exists()|Account.objects.filter(email=name_email).exists():
            account = Account.objects.get(Q(username = name_email)| Q(email = name_email) )
            if (password == account.password):
                request.session['username'] = account.username
                request.session['account_id'] = account.account_id
                role = User.objects.get(username= account.username).role
                data = {'id':account.account_id,'name':account.username,'role':role}
                resp = {'code' : 0, 'msg': 'login successfully','data':data}
                return HttpResponse(json.dumps(resp), content_type="application/json")
            else:
                # wrong password
                resp = {'code' : -1, 'msg': 'password error'}
                return HttpResponse(json.dumps(resp), content_type="application/json")
        else:
            # wrong username
            resp = {'code' : -2, 'msg': 'username does not exit'}
            return HttpResponse(json.dumps(resp), content_type="application/json")
"""
Create account and user
Method: Post
Request: username, email, password, role, first_name, last_name
"""
def add(request):

    try:
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        timestamp = int(now().timestamp())
        if Account.objects.filter(username=username).exists():
            resp = {'code': -1, 'msg': 'username already exist'}
            return HttpResponse(json.dumps(resp), content_type="application/json")
        elif Account.objects.filter(email=email).exists():
            resp = {'code': -2, 'msg': 'email has been registered'}
            return HttpResponse(json.dumps(resp), content_type="application/json")
        else:
            account = Account(username=username, email=email, password=password, status=1, create_date=timestamp)
            user = User(username=username, first_name=first_name, last_name=last_name, role=role, status=1, create_date=timestamp,)
            account.save()
            user.save()
            resp = {'code': 0, 'msg': 'add ok'}
            return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -3, 'msg': 'Unknown error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")

"""
Update account
Method: Post
Request: first_name,last_name,old_password,password
"""

def update(request):
    try:
        fname = request.POST.get('first_name')
        lname = request.POST.get('last_name')
        old_psw = request.POST.get('old_password')
        new_psw = request.POST.get('password')
        username = request.session.get('username', '')
        user = User.objects.get(username = username)
        account = Account.objects.get(username = username)
        if fname!=None:
            user.first_name = fname
            user.save()
        if lname!= None:
            user.last_name = lname
            user.save()
        if old_psw!= None and new_psw!= None:
            if old_psw == account.password:
                account.password = new_psw
                account.save()
            else:
                resp = {'code': -1, 'msg': 'old password wrong'}
                return HttpResponse(json.dumps(resp), content_type="application/json")
        resp = {'code': 0, 'msg': 'account updated'}
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -3, 'msg': 'Unknown Error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")
"""
Get Account
Method: Get
Request: account_id
"""
def account(request):
    try:
        id = request.GET.get('account_id')
        if Account.objects.filter(account_id=id).exists():
            account = Account.objects.get(account_id=id)
            if account.status == 1:
                user = User.objects.get(username=account.username)
                email = account.email
                firstname = user.first_name
                lastname = user.last_name
                username = user.username
                data = {'email': email, 'first_name': firstname, 'last_name': lastname, 'username': username}
                resp = {'code': 0, 'msg': 'ok', 'data': data}
                return HttpResponse(json.dumps(resp), content_type="application/json")
            else:
                resp = {'code': -1, 'msg': 'account has been deleted'}
                return HttpResponse(json.dumps(resp), content_type="application/json")
        else:
            resp = {'code': -2, 'msg': 'account does not exist'}
            return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -3, 'msg': 'Unknown Error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")

"""
Delete Account
Method: Post
Request: account_id
"""
def delete(request):
        try:
            id = request.POST.get('account_id')
            if Account.objects.filter(account_id=id).exists():
                # Account.objects.get(account_id=id).delete()
                # User.objects.get(account_id=id).delete()
                account = Account.objects.get(account_id=id)
                account.status = 0
                user = User.objects.get(username=account.username)
                user.status = 0
                account.save()
                user.save()
                resp = {'code': 0, 'msg': 'account delete'}
                return HttpResponse(json.dumps(resp), content_type="application/json")
            else:
                resp = {'code': -1, 'msg': 'account does not exist'}
                return HttpResponse(json.dumps(resp), content_type="application/json")
        except:
            resp = {'code':-2, 'msg': 'Unknown error'}
            return HttpResponse(json.dumps(resp), content_type="application/json")
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
        timestamp = int(now().timestamp())
        if Account.objects.filter(username=username).exists():
            resp = {'code': -1, 'msg': 'username already exist'}
            return HttpResponse(json.dumps(resp), content_type="application/json")
        else:
            account = Account(username=username, password=password,status=1,create_date=timestamp,)
            user = User(username=username,status=1,create_date=timestamp,)
            account.save()
            user.save()
            resp = {'code': 0, 'msg': 'invite accept'}
            return HttpResponse(json.dumps(resp), content_type="application/json")

