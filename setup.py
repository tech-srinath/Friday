#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'apiai>=1.2.1',
    'gTTS>=1.1.6',
    'PyAudio>=0.2.9',
    'PyYAML>=3.12',
    'SpeechRecognition>=3.4.6',
    'Yapsy>=1.11.223',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='friday',
    version='0.3.3',
    description="An open source virtual assistant.",
    long_description=readme + '\n\n' + history,
    author="Isaac Luke Smith",
    author_email='sentherus@gmail.com',
    url='https://github.com/Zenohm/friday',
    packages=[
        'friday',
    ],
    package_dir={'friday':
                 'friday'},
    entry_points={
        'console_scripts': [
            'friday=friday.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='friday',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
    	'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
