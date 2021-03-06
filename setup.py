from setuptools import setup, find_packages
import sys, os

version = '0.3'

setup(name='ckanext-iati',
      version=version,
      description="CKAN Extension Code for the IATI Registry",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='iati un aid openaid',
      author='Open Knowledge Foundation',
      author_email='info@okfn.org',
      url='http://www.okfn.org',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      namespace_packages=['ckanext'],
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [ckan.plugins]
      iati_approval = ckanext.iati.approval:IatiGroupApprovalExtension
      iati_group_authz = ckanext.iati.authz:IatiGroupAuthzExtension
      iati_package_authz = ckanext.iati.authz:IatiPackageAuthzExtension
      iati_forms = ckanext.iati.plugin:IatiForms
      iati_actions = ckanext.iati.plugin:IatiActions
      iati_license_override = ckanext.iati.plugin:IatiLicenseOverride
      iati_feeds = ckanext.iati.plugin:IatiFeeds

      iati_publishers = ckanext.iati.plugins:IatiPublishers
      iati_datasets = ckanext.iati.plugins:IatiDatasets
      iati_theme = ckanext.iati.plugins:IatiTheme
      iati_csv = ckanext.iati.plugins:IatiCsvImporter

      [paste.paster_command]
      iati-archiver=ckanext.iati.commands:Archiver
      """,
      )
