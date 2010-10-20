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

from django.db import models
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from RestAuth.common.errors import ServiceNotFound

class ServiceUsernameNotValid( BaseException ):
	pass

class ServiceAlreadyExists( BaseException ):
	pass

def check_service_username( name ):
	if type( name ) != str:
		raise ServiceUsernameNotValid( "Name must be of type string" )
	if not name:
		raise ServiceUsernameNotValid( "Service names must be at least one character long" )
	if ':' in name:
		raise ServiceUsernameNotValid( "Service names must not contain a ':'" )

def service_create( name, password, addresses=[] ):
	check_service_username( name )
	
	try:
		service = Service( username=name )
		service.set_password( password )
		service.save()
	except IntegrityError:
		raise ServiceAlreadyExists( "Service already exists. Please use a different name." )

	if addresses:
		service.set_hosts( addresses )

def service_exists( name ):
	if User.objects.filter( username=name ).exists():
		return True
	else:
		return False

def service_get( name ):
	try:
		return Service.objects.get( username=name )
	except User.DoesNotExist:
		raise ServiceNotFound( "Service not found: %s"%(name) )

def service_delete( name ):
	service = service_get( name )
	service.delete()

class ServiceAddress( models.Model ):
	address = models.CharField( max_length=39, unique=True )

	def __unicode__( self ):
		return self.address

class Service( User ):
	hosts = models.ManyToManyField( ServiceAddress )
	
	def verify( self, password, host ):
		if self.check_password( password ) and self.verify_host( host ):
			return True
		else:
			return False

	def verify_host( self, host ):
		if self.hosts.filter( address=host ).exists():
			return True
		else: 
			return False

	def set_hosts( self, addresses=[] ):
		self.hosts.clear()

		for addr in addresses:
			self.add_host( addr )

	def add_host( self, address ):
		addr = ServiceAddress.objects.get_or_create( address=address )[0]
		self.hosts.add( addr )

	def del_host( self, address ):
		try:
			host = ServiceAddress.objects.get( address=addr )
			self.hosts.remove( host )
		except ServiceAddress.DoesNotExist:
			pass

