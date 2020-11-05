from TeamSPBackend.common.config import SALT
from TeamSPBackend.common.utils import mills_timestamp
from TeamSPBackend.common.choices import Status, Roles
from TeamSPBackend.team.models import Team
from TeamSPBackend.subject.models import Subject
from TeamSPBackend.account.models import Account, User
from TeamSPBackend.test.utils import login_helpers

import names


def createGenericAdmin():
    admin_details = {
        "first_name": "admin", "last_name": "admin", "email": "admin@gmail.com"
    }
    createUser(Roles.admin, admin_details)


def createUser(role, user_details):
    """
    user_details:
    - first_name
    - last_name
    - email
    """
    # create account
    timestamp = mills_timestamp()
    username = user_details['first_name']
    password = user_details['first_name']
    email = user_details['email']
    status = Status.valid.value.key
    create_date = timestamp
    update_date = timestamp
    first_name = user_details['first_name']
    last_name = user_details['last_name']
    role = role.value.key
    md5 = login_helpers.encrypt(password)
    account = Account(username=username, email=email, password=md5,
                      status=status, create_date=create_date, update_date=update_date)
    account.save()

    # create user
    user = User(account_id=account.account_id, username=username, first_name=first_name, last_name=last_name,
                role=role, status=status, create_date=create_date, update_date=update_date, email=email)
    user.save()


def generateUserDetails():
    """
    Generate first_name, last_name and email for a user.
    Returns an object:
    {
        "first_name": first_name,
        "last_name": last_name,
        "email": email
    }
    """
    first_name = names.get_first_name()
    last_name = names.get_last_name()
    email = first_name + last_name + "@gmail.com"
    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": email
    }


def createSubject(subject_code, subject_name, coordinator_id):
    subject = Subject(subject_code=subject_code, name=subject_name,
                      coordinator_id=coordinator_id, create_date=mills_timestamp(),
                      status=Status.valid.value.key)
    subject.save()
