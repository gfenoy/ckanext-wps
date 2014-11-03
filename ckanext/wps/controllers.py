from logging import getLogger
import os
import zipfile
import uuid
from pylons import config, Response
from ckan.lib.base import BaseController, c, g, request, \
        response, session, render, config, abort
import ckan.lib.base as base
from ckan.logic import get_action ,check_access, model, NotFound, NotAuthorized
from ckan.common import _

log = getLogger(__name__)


class WpsController(base.BaseController):
    
    def describe(self, id, resource_id, operation):
        log.info("SUCCESS")
        try:
            self._get_context(id, resource_id,operation)
            log.info("SUCCESS")
            return render('wps/describe.html')
        except NotFound:
            abort(404, _('Resource not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read resource %s') % id)

    def execute(self, id, resource_id, operation):
        log.info("SUCCESS")
        try:
            self._get_context(id, resource_id,operation)
            log.info("SUCCESS")
            return render('wps/execute.html')
        except NotFound:
            abort(404, _('Resource not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read resource %s') % id)
        
    
    def _get_context(self, id, resource_id,operation):
        log.info("SUCCESS _get_context")
        context = {'model': model, 'session': model.Session,
                    'user': c.user}
        c.resource = get_action('resource_show')(context,
                                {'id': resource_id})
        c.pkgs = get_action('package_list')(context)
        log.info("SUCCESS _get_context")
        c.wps = get_action("ckanext_wps_describe")(context,
                                                   {'id': resource_id,'p':operation})
        log.info("SUCCESS _get_context")
        c.package = get_action('package_show')(context, {'id': id})
        c.pkg = context['package']
        c.pkg_dict = c.package
