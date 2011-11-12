#!/bin/bash
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

export PYTHONPATH="$PWD"
[ -d ../restauth-common/python ] && export PYTHONPATH="../restauth-common/python:$PYTHONPATH"

rm -f ./RestAuth.sqlite3
python RestAuth/manage.py syncdb --noinput
bin/restauth-service.py add --password=vowi vowi ::1
python RestAuth/manage.py runserver --ipv6
