# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Infrae. All rights reserved.
# See also LICENSE.txt

from setuptools import setup, find_packages
import os

version = '1.3.'

tests_require = [
    'Products.PloneTestCase',
    'mock',
]

setup(name='collective.elasticindex',
      version=version,
      description="Index Plone content in Elastic Search",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='plone index elasticsearch search',
      author='Infrae',
      author_email='info@infrae.com',
      url='https://github.com/infrae/collective.elasticindex',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Acquisition',
          'Products.CMFCore',
          'Products.CMFPlone',
          'Products.statusmessages',
          'plone.app.controlpanel',
          'plone.app.portlets',
          'plone.portlets',
          'pyes',
          'setuptools',
          'transaction',
          'zope.component',
          'zope.formlib',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.schema',
          'zope.traversing',
        ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
