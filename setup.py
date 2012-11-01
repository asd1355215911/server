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

import argparse
import glob
import os
import re
import shutil
import stat
from subprocess import Popen, PIPE
import sys
import time

from distutils.core import setup, Command
from distutils.command.install_data import install_data as _install_data
from distutils.command.build import build as _build
from distutils.command.clean import clean as _clean
from distutils.command.install import install as _install

# Setup environment
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'RestAuth.settings'

common_path = os.path.join('..', 'restauth-common', 'python')
if os.path.exists(common_path):
    sys.path.insert(0, common_path)
    pythonpath = os.environ.get('PYTHONPATH')
    if pythonpath:
        os.environ['PYTHONPATH'] += ':%s' % common_path
    else:
        os.environ['PYTHONPATH'] = common_path

from django.core.management import call_command

from RestAuth.common import cli
from RestAuth.Users.models import user_permissions, prop_permissions
from RestAuth.Groups.models import group_permissions

LATEST_RELEASE = '0.6.0'

if os.path.exists('RestAuth'):
    sys.path.insert(0, 'RestAuth')


def get_version():
    """
    Dynamically get the current version.
    """
    version = LATEST_RELEASE  # default
    if os.path.exists('.version'):  # get from file
        version = open('.version').readlines()[0]
    elif os.path.exists('.git'):  # get from git
        date = time.strftime('%Y.%m.%d')
        cmd = ['git', 'describe', 'master']
        p = Popen(cmd, stdout=PIPE)
        version = p.communicate()[0].decode('utf-8')
    elif os.path.exists('debian/changelog'):  # building .deb
        f = open('debian/changelog')
        version = re.search('\((.*)\)', f.readline()).group(1)
        f.close()

        if ':' in version:  # strip epoch:
            version = version.split(':', 1)[1]
        version = version.rsplit('-', 1)[0]  # strip debian revision
    return version.strip()


class install_data(_install_data):
    """
    Improve the install_data command so it can also copy directories
    """
    def custom_copy_tree(self, src, dest):
        base = os.path.basename(src)
        dest = os.path.normpath("%s/%s/%s" % (self.install_dir, dest, base))
        if os.path.exists(dest):
            return
        ignore = shutil.ignore_patterns('.svn', '*.pyc')
        print("copying %s -> %s" % (src, dest))
        shutil.copytree(src, dest, ignore=ignore)

    def run(self):
        for dest, nodes in self.data_files:
            dirs = [node for node in nodes if os.path.isdir(node)]
            for src in dirs:
                self.custom_copy_tree(src, dest)
                nodes.remove(src)
        _install_data.run(self)


class install(_install):
    def run(self):
        _install.run(self)

        # write symlink for restauth-manage.py
        target = os.path.join(self.install_scripts, 'restauth-manage.py')
        source = os.path.join(
            os.path.abspath(self.install_purelib),
            'RestAuth', 'manage.py'
        )
        if not os.path.exists(target):
            os.symlink(source, target)

        # set execute permissions:
        mode = os.stat(source).st_mode
        os.chmod(source, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

added_options = [
    ('prefix=', None, 'installation prefix'),
    ('exec-prefix=', None, 'prefix for platform-specific files')
]


class clean(_clean):
    def initialize_options(self):
        _clean.initialize_options(self)

    def run(self):
        _clean.run(self)

        # clean sphinx documentation:
        cmd = ['make', '-C', 'doc', 'clean']
        p = Popen(cmd)
        p.communicate()

        coverage = os.path.join('doc', 'coverage')
        generated = os.path.join('doc', 'gen')

        if os.path.exists(coverage):
            print('rm -r %s' % coverage)
            shutil.rmtree(os.path.join('doc', 'coverage'))
        if os.path.exists(generated):
            print('rm -r %s' % generated)
            shutil.rmtree(generated)
        if os.path.exists('MANIFEST'):
            print('rm MANIFEST')
            os.remove('MANIFEST')


class version(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print(get_version())


class build_doc_meta(Command):
    user_options = [
        ('target=', 't', 'What distribution to build for'),
    ]

    def __init__(self, *args, **kwargs):
        Command.__init__(self, *args, **kwargs)

        # generate files for cli-scripts:
        cli.service_parser.prog = '|bin-restauth-service|'
        cli.user_parser.prog = '|bin-restauth-user|'
        cli.group_parser.prog = '|bin-restauth-group|'
        cli.import_parser.prog = '|bin-restauth-import|'

        # create necesarry folders:
        if not os.path.exists('doc/_static'):
            os.mkdir('doc/_static')
        if not os.path.exists('doc/gen'):
            os.mkdir('doc/gen')

        for parser, name in [(cli.service_parser, 'restauth-service'),
                             (cli.user_parser, 'restauth-user'),
                             (cli.group_parser, 'restauth-group'),
                             (cli.import_parser, 'restauth-import')]:

            for suffix in ['usage', 'commands', 'parameters']:
                filename = 'doc/gen/%s-%s.rst' % (name, suffix)
                if self.should_generate(cli.__file__, filename):
                    func = getattr(cli, 'write_%s' % suffix)
                    func(parser, filename, name)

        # generate permissions:
        self.write_perm_table('users', user_permissions)
        self.write_perm_table('properties', prop_permissions)
        self.write_perm_table('groups', group_permissions)

        pythonpath = os.environ.get('PYTHONPATH')
        if pythonpath:
            os.environ['PYTHONPATH'] += ':.'
        else:
            os.environ['PYTHONPATH'] = '.'
        common_path = os.path.abspath(
            os.path.join('..', 'restauth-common', 'python'))
        if os.path.exists(common_path):
            os.environ['PYTHONPATH'] += ':%s' % common_path

        version = get_version()
        os.environ['SPHINXOPTS'] = '-D release=%s -D version=%s' \
            % (version, version)
        os.environ['RESTAUTH_LATEST_RELEASE'] = LATEST_RELEASE

    def write_perm_table(self, suffix, perms):
        f = open('doc/gen/restauth-service-permissions-%s.rst' % suffix, 'w')

        col_1_header = 'permission'
        col_2_header = 'description'

        col_1_length = max([len(x) for x, y in perms] + [len(col_1_header)])
        col_2_length = max([len(y) for x, y in perms] + [len(col_2_header)])
        f.write('%s %s\n' % ('=' * col_1_length, '=' * col_2_length))
        f.write('%s ' % col_1_header.ljust(col_1_length, ' '))
        f.write('%s\n' % col_2_header.ljust(col_2_length, ' '))
        f.write('%s %s\n' % ('=' * col_1_length, '=' * col_2_length))

        for codename, name in perms:
            f.write('%s ' % codename.ljust(col_1_length, ' '))
            f.write('%s\n' % name.ljust(col_2_length, ' '))

        f.write('%s %s\n' % ('=' * col_1_length, '=' * col_2_length))

        f.close()

    def should_generate(self, source, generated):
        if not os.path.exists(os.path.dirname(generated)):
            os.mkdirs(os.path.dirname(generated))
            return True
        if not os.path.exists(generated):
            return True
        if os.stat(source).st_mtime > os.stat(generated).st_mtime:
            return True
        return False

    def initialize_options(self):
        self.target = None

    def finalize_options(self):
        if self.target:
            os.environ['SPHINXOPTS'] += ' -t %s' % self.target


class build_doc(build_doc_meta):
    description = "Build documentation as HTML and man-pages"

    def run(self):
        cmd = ['make', '-C', 'doc', 'man', 'html']
        p = Popen(cmd)
        p.communicate()


class build_html(build_doc_meta):
    description = "Build HTML documentation"

    def run(self):
        cmd = ['make', '-C', 'doc', 'html']
        p = Popen(cmd)
        p.communicate()


class build_man(build_doc_meta):
    description = "Build man-pages"

    def run(self):
        cmd = ['make', '-C', 'doc', 'man']
        p = Popen(cmd)
        p.communicate()


class build(_build):
    def initialize_options(self):
        """
        Modify this class so that we also understand --install-dir.
        """
        _build.initialize_options(self)
        self.prefix = None
        self.exec_prefix = None

    sub_commands = [
        ('build_man', lambda self: True),
        ('build_man', lambda self: True)
    ] + _build.sub_commands
    user_options = _build.user_options + added_options


class test(Command):
    user_options = [
        ('app=', None, 'Only test the specified app'),
    ]

    def initialize_options(self):
        self.app = None

    def finalize_options(self):
        pass

    def run(self):
        if self.app:
            print(self.app)
            call_command('test', self.app)
        else:
            call_command('test', 'Users', 'Groups', 'Test', 'Services',
                         'common')


class coverage(Command):
    description = "Run test suite and generate code coverage analysis."
    user_options = [
        ('output-dir=', 'o', 'Output directory for coverage analysis'),
    ]

    def initialize_options(self):
        self.dir = 'doc/coverage'

    def finalize_options(self):
        pass

    def run(self):
        try:
            import coverage
        except ImportError:
            print("You need coverage.py installed.")
            return

        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

        cov = coverage.coverage(
            cover_pylib=False, include='RestAuth/*',
            omit=['*tests.py', '*testdata.py', '*settings.py'])
        cov.start()

        call_command('test', 'Users', 'Groups', 'Test', 'Services', 'common')

        cov.stop()
        cov.html_report(directory=self.dir)
#        cov.report()


class testserver(Command):
    description = "Run a testserver on http://[::1]:8000"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import django
        from django.core import management

        # this causes django to use stock syncdb instead of South-version
        management.get_commands()
        management._commands['syncdb'] = 'django.core'

        fixture = 'RestAuth/fixtures/testserver.json'
        if django.VERSION[:2] == (1, 4):
            # see https://github.com/django/django/commit/bb4452f212e211bca7b6b57904d59270ffd7a503
            from django.db import connection as conn

            # Create a test database.
            db_name = conn.creation.create_test_db()

            # Import the fixture data into the test database.
            call_command('loaddata', fixture)

            use_threading = conn.features.test_db_allows_multiple_connections
            call_command(
                'runserver',
                shutdown_message='Testserver stopped.',
                use_reloader=False,
                use_ipv6=True,
                use_threading=use_threading
            )
        else:
            call_command('testserver', fixture, use_ipv6=True)


class prepare_debian_changelog(Command):
    description = "prepare debian/changelog file"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if not os.path.exists('debian/changelog'):
            sys.exit(0)

        version = get_version()
        cmd = ['sed', '-i', '1s/(.*)/(%s-1)/' % version, 'debian/changelog']
        p = Popen(cmd)
        p.communicate()

setup(
    name='RestAuth',
    version=str(get_version()),
    description='RestAuth web service',
    author='Mathias Ertl',
    author_email='mati@restauth.net',
    url='https://restauth.net',
    packages=['RestAuth', 'RestAuth.common',
    'RestAuth.Services', 'RestAuth.Services.migrations',
        'RestAuth.Groups', 'RestAuth.Groups.migrations',
        'RestAuth.Users', 'RestAuth.Users.migrations',
        'RestAuth.common', 'RestAuth.Test'],
    scripts=[
        'bin/restauth-service.py', 'bin/restauth-user.py',
        'bin/restauth-group.py', 'bin/restauth-import.py',
    ],
    data_files=[
        ('share/restauth', ['wsgi']),
        ('share/doc/restauth', ['AUTHORS', 'COPYING', 'COPYRIGHT']),
    ],
    cmdclass={
        'build': build, 'clean': clean,
        'build_doc': build_doc, 'build_man': build_man,
        'build_html': build_html,
        'install': install, 'install_data': install_data,
        'version': version,
        'test': test, 'coverage': coverage, 'testserver': testserver,
        'prepare_debian_changelog': prepare_debian_changelog,
    },
)
