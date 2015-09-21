#!/usr/bin/env python
""" Setup to allow pip installs of pok-eco module """

from setuptools import setup

setup(
    name='pok-eco',
    version='0.1.0',
    description='POK-ECO Integrations ',
    author='METID - Politecnico di Milano',
    url='http://www.metid.polimi.it',
    license='AGPL',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    packages=['oai', 'ecoapi', 'xapi'],
    dependency_links=["https://github.com/infrae/pyoai/archive/2.4.4.zip#egg=pyoai==2.4.4"],
    install_requires=[
        "Django >= 1.4, < 1.5",
        "django-celery==3.1.16"
    ]
)
