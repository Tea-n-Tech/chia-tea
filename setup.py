#!/usr/bin/env python

import unittest
from setuptools import setup, find_packages


def collect_tests():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('.', pattern='test_*.py')
    return test_suite


def get_requirements():
    with open("requirements.txt", "r") as fp:
        requirements = [line.strip() for line in fp if line.strip()]
        print(requirements)
        return requirements


def main():

    setup(name='chia-tea',
          version='0.1.0',
          description='A library dedicated to chia-blockchain farmer.',
          author="Tea 'n Tech",
          url='https://www.youtube.com/channel/UCba194Pls_bHSqWoWMGoyzA',
          license="BSD-3",
          packages=find_packages(),
          test_suite='setup.collect_tests',
          install_requires=get_requirements(),
          zip_safe=False,
          classifiers=[
              'Development Status :: 3 - Alpha',
              'Environment :: Console',
              'Topic :: Scientific/Engineering',
              'Intended Audience :: Developers',
              'Intended Audience :: Information Technology',
              'Intended Audience :: System Administrators',
              'License :: OSI Approved :: BSD License',
              'Natural Language :: English',
              'Operating System :: Microsoft :: Windows',
              'Operating System :: POSIX',
              'Programming Language :: PL/SQL',
              'Topic :: Database',
              'Topic :: Communications :: Chat',
              'Topic :: System :: Monitoring',
              'Programming Language :: Python :: 3.7',
              'Programming Language :: Python :: 3.8',
              'Programming Language :: Python :: 3.9',
          ]
          )


if __name__ == "__main__":
    main()
