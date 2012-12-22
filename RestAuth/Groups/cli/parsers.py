#!/usr/bin/env python
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

from argparse import ArgumentParser

from RestAuth.common.cli.parsers import user_parser
from RestAuth.common.cli.actions import ServiceAction
from RestAuth.Groups.cli.actions import GroupnameAction
from RestAuth.Groups.cli.helpers import print_by_service, get_group


service_opt_parser = ArgumentParser(add_help=False)
service_opt_parser.set_defaults(create_service=False)
service_opt_parser.add_argument('--service', action=ServiceAction,
                                help="Act as if %(prog)s was SERVICE.")

group_arg_parser = ArgumentParser(add_help=False, parents=[service_opt_parser])
group_arg_parser.add_argument('group', action=GroupnameAction,
                              help="The name of the group.")
group_arg_parser.set_defaults(create_group=False)

subgroup_parser = ArgumentParser(add_help=False)
subgroup_parser.add_argument('subgroup', help='The name of the subgroup.')
subgroup_parser.add_argument(
    '--sub-service', metavar='SUBSERVICE', action=ServiceAction,
    help='Assume that the named subgroup is from SUBSERVICE.'
)

# actual parser
desc = """%(prog)s manages groups in RestAuth. Groups can have users and
groups as members, handing down users to member groups. For a group to be
visible to a service, it must be associated with it. It is possible for a group
to not be associated with any service, which is usefull for e.g. a group
containing global super-users. Valid actions are help, add, list, view,
add-user, add-group, remove, remove-user, and remove-group."""
parser = ArgumentParser(description=desc)

group_subparsers = parser.add_subparsers(
    title="Available actions", dest='action',
    description="Use '%(prog)s action --help' for more help on each action.")

# add:
group_add_parser = group_subparsers.add_parser(
    'add', help="Add a new group.", parents=[group_arg_parser],
    description="Add a new group.")
group_add_parser.set_defaults(create_group=True)

# ls:
group_ls_parser = group_subparsers.add_parser(
    'ls', parents=[service_opt_parser],
    help="List all groups.", description="List all groups.")

# view:
group_subparsers.add_parser(
    'view', help="View details of a group.", parents=[group_arg_parser],
    description="View details of a group."
)

# add-user
group_subparsers.add_parser(
    'add-user', parents=[group_arg_parser, user_parser],
    help="Add a user to a group.", description="Add a user to a group."
)
group_subparsers.add_parser(
    'add-group', parents=[group_arg_parser, subgroup_parser],
    help="""Make a group a subgroup to another group.""",
    description='Make a group a subgroup of another group. The subgroup will '
    'inherit all memberships from the parent group.'
)
group_subparsers.add_parser(
    'rm-user', parents=[group_arg_parser, user_parser],
    help="Remove a user from a group.",
    description="Remove a user from a group."
)
group_subparsers.add_parser(
    'rm-group', parents=[group_arg_parser, subgroup_parser],
    help='Remove a subgroup from a group.',
    description='Remove a subgroup from a group. The subgroup will no longer '
    'inherit all memberships from a parent group.'
)
group_subparsers.add_parser(
    'rm', parents=[group_arg_parser], help="Remove a group.",
    description="Remove a group."
)
