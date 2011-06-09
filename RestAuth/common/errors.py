# This file is part of RestAuth (http://fs.fsinf.at/wiki/RestAuth).
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

from RestAuthCommon.error import PreconditionFailed, ResourceConflict

class PasswordInvalid( PreconditionFailed ):
	pass

class UsernameInvalid( PreconditionFailed ):
	pass

class UserExists( ResourceConflict ):
	pass

class PropertyExists( ResourceConflict ):
	pass

class GroupExists( ResourceConflict ):
	pass