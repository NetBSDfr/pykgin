from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='pykgin',
      version=version,
      description="A basic API for pkgin",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='netbsd pkgin pykgin',
      author='Sylvain Mora',
      author_email='sylvain.mora@solevis.net',
      url='http://pykgin.solevis.net',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
