import hashlib
from django.test import Client
from TeamSPBackend.team.models import Team
from TeamSPBackend.account.models import Account
from TeamSPBackend.common.config import SALT


def create_test_account(username, email, password, status, create_date, update_date):
    md5 = encrypt(password)
    account = Account(username=username, email=email, password=md5,
                      status=status, create_date=create_date, update_date=update_date)
    account.save()


def login(username, password):
    credentials = {
        'username': username,
        'password': password
    }
    client = Client()
    response = client.post('/api/v1/account/login',
                           data=credentials, content_type="application/json")
    print("first print" + str(response.json()))


def encrypt(password):
    password = password + SALT
    md5 = hashlib.sha3_256(password.encode()).hexdigest()
    return md5
