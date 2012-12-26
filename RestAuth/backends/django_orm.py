from datetime import datetime

from django.db import transaction
from django.db.utils import IntegrityError

from RestAuth.backends.base import GroupBackend
from RestAuth.backends.base import PropertyBackend
from RestAuth.backends.base import UserBackend
from RestAuth.common.errors import UserExists

from RestAuth.Users.models import ServiceUser as User


class DjangoUserBackend(UserBackend):
    def list(self):
        return list(User.objects.values_list('username', flat=True))

    def _create(self, username, password=None, properties=None):
        try:
            user = User(username=username)
            if password is not None and password != '':
                user.set_password(password)
            user.save()
        except IntegrityError:
            raise UserExists("A user with the given name already exists.")

        if properties is not None:
            for key, value in properties.iteritems():
                user.set_property(key, value)

        if properties is None or 'date joined' not in properties:
            stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user.set_property('date joined', stamp)
        return user

    def create(self, username, password=None, properties=None, dry=False):
        if dry:
            raise NotImplementedError
        else:
            with transaction.commit_on_success():
                return self._create(username, password, properties)

    def check_password(self, username, password):
        # If User.DoesNotExist: 404 Not Found
        user = User.objects.only('password').get(username=username)

        return user.check_password(password)

    def exists(self, username):
        return User.objects.filter(username=username).exists()

    def set_password(self, username, password):
        # If User.DoesNotExist: 404 Not Found
        user = User.objects.only('id').get(username=username)
        if password is not None and password != '':
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save()

    def remove(self, username):
        qs = User.objects.filter(username=username)
        if qs.exists():
            qs.delete()
        else:
            raise User.DoesNotExist


class DjangoPropertyBackend(PropertyBackend):
    def list(self, username):
        # If User.DoesNotExist: 404 Not Found
        user = User.objects.only('id').get(username=name)
        return user.get_properties()

    def create(self, username, key, value):
        raise NotImplementedError

    def get(self, username, key):
        raise NotImplementedError

    def set(self, username, key, value):
        raise NotImplementedError

    def set_multiple(self, username, props):
        raise NotImplementedError

    def remove(self, username, key):
        raise NotImplementedError

class DjangoGroupBackend(GroupBackend):
    def create(self, service, groupname):
        raise NotImplementedError

    def exists(self, service, groupname):
        raise NotImplementedError

    def add_user(self, service, groupname, username):
        raise NotImplementedError

    def users(self, service, groupname):
        raise NotImplementedError

    def member(self, service, groupname, username):
        raise NotImplementedError

    def rm_user(self, service, groupname, username):
        raise NotImplementedError

    def add_subgroup(self, service, groupname, subservice, subgroupname):
        raise NotImplementedError

    def subgroups(self, service, groupname, subservice):
        raise NotImplementedError

    def rm_subgroup(self, service, groupname, subservice, subgroupname):
        raise NotImplementedError

    def remove(self, service, groupname):
        raise NotImplementedError
