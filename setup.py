# -*- coding: utf-8 -*-
import os
from setuptools import setup


with open(os.path.join(os.path.dirname(__file__), 'README.txt')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='e89-push-messaging',
    version='1.0.11',
    packages=['e89_push_messaging'],
    include_package_data=True,
    license='BSD License',  # example license
    description='Aplicação para envio de notificações push - Estúdio 89.',
    long_description=README,
    url='http://www.estudio89.com.br/',
    author='Luccas Correa',
    author_email='luccascorrea@estudio89.com.br',
    install_requires=['e89_security>=1.0.1'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)