#!/usr/bin/env python

import os

import setuptools


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setuptools.setup(
    name='Turplanlegger',
    version=read('VERSION'),
    description='Turplanlegger python API',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/sixcare/turplanlegger',
    license='MIT',
    author='Are Schjetne',
    author_email='are.schjetne@gmail.com',
    packages=setuptools.find_packages(exclude=['tests']),
    install_requires=[
        'Flask>=2.0.1',
        'Flask-Compress>=1.4.0',
        'psycopg2',
    ],
    include_package_data=True,
    zip_safe=False,
    keywords='trip, planning',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Programming Language :: Python :: 3.10;',
    ],
    python_requires='>=3.10'
)
