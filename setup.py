from setuptools import setup, find_packages
import sys

import lina

setup(
    name = "Lina",
    version = lina.__version__,
    packages = find_packages (exclude=['*.test', 'test.*', '*.test.*']),

    setup_requires=['pytest-runner'],
    test_requires=['pytest'],

    install_requires = [],

    author = "Matthäus G. Chajdas",
    author_email = "dev@anteru.net",
    description = "Text template library",
    license = "BSD",
    keywords = [],
    url = "http://shelter13.net/projects/Lina",

    classifiers=[
        'Development Status :: 6 - Mature',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Pre-processors',
    ]
)
