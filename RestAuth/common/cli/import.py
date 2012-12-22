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

from argparse import ArgumentParser
import argparse
import sys

##############################
### restauth-import parser ###
##############################
import_desc = "Import user data from another system."
import_parser = ArgumentParser(description=import_desc)

import_parser.add_argument(
    '--gen-passwords', action='store_true', default=False,
    help="Generate passwords where missing in input data and print them to "
    "stdout."
)
import_parser.add_argument(
    '--overwrite-passwords', action='store_true', default=False,
    help='Overwrite passwords of already existing services or users if the'
    'input data contains a password. (default: %(default)s)'
)
import_parser.add_argument(
    '--overwrite-properties', action='store_true', default=False,
    help='Overwrite already existing properties of users. (default: '
    '%(default)s)'
)
import_parser.add_argument(
    '--skip-existing-users', action='store_true', default=False, help=
    'Skip users completely if they already exist. If not set, passwords and '
    'properties are overwritten if their respective --overwrite-... argument '
    'is given.'
)
import_parser.add_argument(
    '--skip-existing-groups', action='store_true', default=False, help=
    'Skip groups completely if they already exist. If not set, users and '
    'subgroups will be added to the list.'
)
import_parser.add_argument(
    '--using', default=None, metavar="ALIAS",
    help="Use different database alias. (UNTESTED!)"
)

import_parser.add_argument(
    'file', nargs='?', type=argparse.FileType('r'), default=sys.stdin)