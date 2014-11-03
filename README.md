CKAN WPS Extension
============================


Overview
--------

CKANEXT-WPS is a CKAN extension that allows users to access OGC WPS
capabilities and publish execution results.


Installation
------------

    $ git clone https://github.com/gfenoy/ckanext-wps.git
    $ python setup.py develop
    $ pip install -r pip-requirements.txt


Configuration
-------------

**1.  Enabling Vector Storer**

  To enable the Vector Storer Extension add this to ckan plugins in the config file :
 
        ckan.plugins = vectorstorer

**2.  CKANEXT-WPS config options**

  The following should be set in the CKAN config :

        # ckanext-wps settings
		ckanext-wps.target_dataset=(e.g. CKAN Resource identifier)

  The default target dataset to store the WPS Execution result.
