import datetime
import json
import random

from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.hashers import check_password

from TeamSPBackend.account.models import Account, User

"""
Account APIs
url: api/version/account/...
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
            user = Account.objects.get(Q(username = name_email)| Q(email = name_email) )
            if (password == user.password):
                request.session['username'] = user.username
                request.session['accountId'] = user.accountId
                role = User.objects.get(accountId= user.accountId).role
                data = {'id':user.accountId,'name':user.username,'role':role}
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
        if Account.objects.filter(username=username).exists():
            resp = {'code': -1, 'msg': 'username already exist'}
            return HttpResponse(json.dumps(resp), content_type="application/json")
        elif Account.objects.filter(email=email).exists():
            resp = {'code': -2, 'msg': 'email has been registered'}
            return HttpResponse(json.dumps(resp), content_type="application/json")
        else:
            nowTime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            randomNum = random.randint(0, 100)
            if randomNum <= 10:
                randomNum = str(0) + str(randomNum)
            id = str(nowTime) + str(randomNum)
            account = Account(accountId = id, username = username, email = email, password = password)
            account.save()
            user = User(accountId = id,username = username,first_name = first_name, last_name = last_name, role = role)
            user.save()
            resp = {'code': 0, 'msg': 'add ok'}
            return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -3, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")

"""
Update account
Method: Post
Request: first_name,last_name,old_password,password
"""

def update(request):
    if request.method == 'POST':
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
"""
Get Account
Method: Get
Request: accountId
"""
def account(request):
    if request.method == 'GET':
        id =  request.GET.get('accountId')
        print(id)
        try:
            user = User.objects.get(accountId=id)
            account = Account.objects.get(accountId=id)
            email = account.email
            firstname = user.first_name
            lastname = user.last_name
            username = user.username
            data = {'email': email, 'first_name': firstname, 'last_name': lastname, 'username': username}
            resp = {'code': 0, 'msg': 'ok', 'data': data}
            return HttpResponse(json.dumps(resp), content_type="application/json")
        except:
            resp = {'code': -1, 'msg': 'fail'}
            return HttpResponse(json.dumps(resp), content_type="application/json")

"""
Delete Account
Method: Post
Request: accountId
"""
def delete(request):
        try:
            id = request.POST.get('accountId')
            if Account.objects.filter(accountId=id).exists():
                Account.objects.get(accountId=id).delete()
                User.objects.get(accountId=id).delete()
                resp = {'code': 0, 'msg': 'account delete'}
                return HttpResponse(json.dumps(resp), content_type="application/json")
            else:
                resp = {'code': -1, 'msg': 'account does not exist'}
                return HttpResponse(json.dumps(resp), content_type="application/json")
        except:
            resp = {'code':-2, 'msg': 'error'}
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
        if Account.objects.filter(username=username).exists():
            resp = {'code': -1, 'msg': 'username already exist'}
            return HttpResponse(json.dumps(resp), content_type="application/json")
        else:
            nowTime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            randomNum = random.randint(0, 100)
            if randomNum <= 10:
                randomNum = str(0) + str(randomNum)
            id = str(nowTime) + str(randomNum)
            account = Account(accountId=id, username=username, password=password)
            account.save()
            user = User(accountId=id, username=username)
            user.save()
            resp = {'code': 0, 'msg': 'invite accept'}
            return HttpResponse(json.dumps(resp), content_type="application/json")

