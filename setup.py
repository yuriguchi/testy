# TestY TMS - Test Management System
# Copyright (C) 2024 KNS Group LLC (YADRO)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Also add information on how to contact you by electronic and paper mail.
#
# If your software can interact with users remotely through a computer
# network, you should also make sure that it provides a way for users to
# get its source.  For example, if your program is a web application, its
# interface could display a "Source" link that leads users to an archive
# of the code.  There are many ways you could offer source, and different
# solutions will be better for different programs; see section 13 for the
# specific requirements.
#
# You should also get your employer (if you work as a programmer) or school,
# if any, to sign a "copyright disclaimer" for the program, if necessary.
# For more information on this, and how to apply and follow the GNU AGPL, see
# <http://www.gnu.org/licenses/>.
from setuptools import find_packages, setup

setup(
    name='testy',
    version='2.0.5',
    python_requires='==3.11.9',
    description='Test management system',
    packages=find_packages(
        exclude=['tests*'],
    ),
    install_requires=[
        'django==4.2.13',
        'python-dotenv==0.21.0',
        'djangorestframework==3.15.1',
        'django-simple-history==3.1.1',
        'django_filter==22.1',
        'drf-yasg==1.21.4',
        'django-filter==22.1',
        'redis==4.6.0',
        'celery==5.2.7',
        'celery-progress==0.1.3',
        'django-celery-beat==2.5.0',
        'django-redis==5.2.0',
        'pytimeparse==1.1.8',
    ],
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11.9',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development',
    ],
    license='GNU Affero General Public License v3 or later (AGPLv3+)',
    license_file='LICENSE',
)
