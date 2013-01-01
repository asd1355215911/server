# -*- coding: utf-8 -*-
#
# This file is part of RestAuth (https://restauth.net).
#
# RestAuth is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RestAuth is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RestAuth.  If not, see <http://www.gnu.org/licenses/>.

"""
This module implements all HTTP queries to ``/group/*``.
"""

import logging

from django.conf import settings
from django.http import HttpResponseForbidden

from RestAuth.common.errors import UserNotFound
from RestAuth.common.errors import GroupNotFound
from RestAuth.common.responses import HttpResponseCreated
from RestAuth.common.responses import HttpResponseNoContent
from RestAuth.common.responses import HttpRestAuthResponse
from RestAuth.common.types import get_dict
from RestAuth.common.utils import import_path
from RestAuth.common.views import (RestAuthView, RestAuthResourceView,
                                   RestAuthSubResourceView)

user_backend = import_path(getattr(
            settings, 'USER_BACKEND',
            'RestAuth.backends.django_orm.DjangoUserBackend'
))[0]()
group_backend = import_path(getattr(
            settings, 'GROUP_BACKEND',
            'RestAuth.backends.django_orm.DjangoGroupBackend'
))[0]()


class GroupsView(RestAuthView):
    """
    Handle requests to ``/groups/``.
    """
    log = logging.getLogger('groups')
    http_method_names = ['get', 'post']

    def get(self, request, largs):
        """
        Get a list of groups or, if called with the 'user' query parameter,
        a list of groups where the user is a member of.
        """
        username = request.GET.get('user', None)
        if username is None or username == '':
            if not request.user.has_perm('Groups.groups_list'):
                return HttpResponseForbidden()

            groups = group_backend.list(service=request.user)
        else:
            if not request.user.has_perm('Groups.groups_for_user'):
                return HttpResponseForbidden()

            # Get all groups of a user
            user = user_backend.get(username=username.lower())
            groups = group_backend.list(service=request.user, user=user)

        return HttpRestAuthResponse(request, groups)

    def post(self, request, largs, dry=False):
        """
        Create a new group.
        """
        if not request.user.has_perm('Groups.group_create'):
            return HttpResponseForbidden()

        # If BadRequest: 400 Bad Request
        groupname = get_dict(request, [u'group'])
        groupname = groupname.lower()

        # If ResourceExists: 409 Conflict
        group = group_backend.create(service=request.user, name=groupname,
                                     dry=dry)

        self.log.info('%s: Created group', group.name, extra=largs)
        return HttpResponseCreated(request, 'groups.group', name=group.name)  # Created


class GroupHandlerView(RestAuthResourceView):
    """
    Handle requests to ``/groups/<group>/``.
    """
    log = logging.getLogger('groups.group')
    http_method_names = ['get', 'delete']

    def get(self, request, largs, name):
        """
        Verify that a group exists.
        """
        if not request.user.has_perm('Groups.group_exists'):
            return HttpResponseForbidden()

        if group_backend.exists(service=request.user, name=name):
            return HttpResponseNoContent()
        else:
            raise GroupNotFound(name)

    def delete(self, request, largs, name):
        """
        Delete a group.
        """
        if not request.user.has_perm('Groups.group_delete'):
            return HttpResponseForbidden()

        group_backend.remove(service=request.user, name=name)
        self.log.info("Deleted group", extra=largs)
        return HttpResponseNoContent()


class GroupUsersIndex(RestAuthResourceView):
    """
    Handle requests to ``/groups/<group>/users/``.
    """
    log = logging.getLogger('groups.group.users')
    http_method_names = ['get', 'post']

    def get(self, request, largs, name):
        """
        Get all users in a group.
        """
        if not request.user.has_perm('Groups.group_users'):
            return HttpResponseForbidden()

        # If GroupNotFound: 404 Not Found
        group = group_backend.get(service=request.user, name=name)

        users = group_backend.members(group=group)
        return HttpRestAuthResponse(request, users)

    def post(self, request, largs, name):
        """
        Add a user to a group.
        """
        if not request.user.has_perm('Groups.group_add_user'):
            return HttpResponseForbidden()

        # If BadRequest: 400 Bad Request
        username = get_dict(request, [u'user']).lower()

        # If GroupNotFound: 404 Not Found
        group = group_backend.get(service=request.user, name=name)

        # If UserNotFound: 404 Not Found
        user = user_backend.get(username=username)

        group_backend.add_user(group=group, user=user)

        self.log.info('Add user "%s"', username, extra=largs)
        return HttpResponseNoContent()


class GroupUserHandler(RestAuthSubResourceView):
    """
    Handle requests to ``/groups/<group>/users/<user>/``.
    """
    log = logging.getLogger('groups.group.users.user')
    http_method_names = ['get', 'delete']

    def get(self, request, largs, name, subname):
        """
        Verify that a user is in a group.
        """
        if not request.user.has_perm('Groups.group_user_in_group'):
            return HttpResponseForbidden()

        # If GroupNotFound: 404 Not Found
        group = group_backend.get(service=request.user, name=name)

        # If UserNotFound: 404 Not Found
        user = user_backend.get(username=subname)

        if group_backend.is_member(group=group, user=user):
            return HttpResponseNoContent()
        else:
            raise UserNotFound(subname)  # 404 Not Found

    def delete(self, request, largs, name, subname):
        """
        Remove a user from a group.
        """
        if not request.user.has_perm('Groups.group_remove_user'):
            return HttpResponseForbidden()

        # If GroupNotFound: 404 Not Found
        group = group_backend.get(service=request.user, name=name)

        # If UserNotFound: 404 Not Found
        user = user_backend.get(username=subname)

        group_backend.rm_user(group=group, user=user)
        self.log.info('Remove user from group', extra=largs)
        return HttpResponseNoContent()


class GroupGroupsIndex(RestAuthResourceView):
    """
    Handle requests to ``/groups/<group>/group/``.
    """
    log = logging.getLogger('groups.group.groups')
    http_method_names = ['get', 'post']

    def get(self, request, largs, name):
        """
        Get a list of sub-groups
        """
        if not request.user.has_perm('Groups.group_groups_list'):
            return HttpResponseForbidden()

        # If GroupNotFound: 404 Not Found
        group = group_backend.get(service=request.user, name=name)

        groups = group_backend.subgroups(group=group)
        return HttpRestAuthResponse(request, groups)

    def post(self, request, largs, name):
        """
        Add a sub-group.
        """
        if not request.user.has_perm('Groups.group_add_group'):
            return HttpResponseForbidden()

        # If BadRequest: 400 Bad Request
        subname = get_dict(request, [u'group']).lower()

        # If GroupNotFound: 404 Not Found
        group = group_backend.get(service=request.user, name=name)
        subgroup = group_backend.get(service=request.user, name=subname)

        group_backend.add_subgroup(group=group, subgroup=subgroup)

        self.log.info('Add subgroup "%s"', subname, extra=largs)
        return HttpResponseNoContent()


class GroupGroupHandler(RestAuthSubResourceView):
    """
    Handle requests to ``/groups/<meta-group>/group/<sub-group>/``.
    """
    log = logging.getLogger('groups.group.groups.subgroup')
    http_method_names = ['delete']

    def delete(self, request, largs, name, subname):
        """
        Remove a subgroup from a group.
        """
        if not request.user.has_perm('Groups.group_remove_group'):
            return HttpResponseForbidden()

        # If GroupNotFound: 404 Not Found
        group = group_backend.get(service=request.user, name=name)
        subgroup = group_backend.get(service=request.user, name=subname)

        group_backend.rm_subgroup(group=group, subgroup=subgroup)
        self.log.info('Remove subgroup %s', subname, extra=largs)
        return HttpResponseNoContent()
