from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
	name='ckanext-wps',
	version=version,
	description="A CKAN Extension to add the WPS capabilities.",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='G\xc3\xa9rald Fenoy',
	author_email='gerald.fenoy@geolabs.fr',
	url='http://www.geolabs.fr',
	license='MIT/X11',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.wps'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
        [ckan.plugins]
	wps_preview=ckanext.wps.plugin:WPSPreview
	# Add plugins here, eg
	# myplugin=ckanext.wps:PluginClass
	""",
)
