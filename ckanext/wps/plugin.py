from logging import getLogger
import ckan.plugins as plugins
import ckanext.wps.logic.actions as wpsclient

log = getLogger(__name__)

# Our custom template helper function.
def capabilities_helper():
    '''An example template helper function.'''
    # Just return some example text.
    import urllib2
    import owslib.wps
    from owslib.wps import WebProcessingService, monitorExecution
    response = urllib2.urlopen(str(plugins.toolkit.c.resource['origin_url']))
    tmp=response.read()
    wps=WebProcessingService(str(plugins.toolkit.c.resource['origin_url']))
    #wps.getcapabilities(tmp)
    wps.processes1=wps.processes#[:len(wps.processes)/2]
    wps.provider.contact.keys=dir(wps.provider.contact)
    wps.resource=plugins.toolkit.c.resource
    wps.package=plugins.toolkit.c.package
    return wps

def printDir(arg=None):
    return dir(arg)

class WPSPreview(plugins.SingletonPlugin):

    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.ITemplateHelpers)
    #plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IResourcePreview, inherit=True)
    
    myformat=['wps']
        
    def before_map(self, map):
        map.connect('{action}', '/dataset/{id}/resource/{resource_id}/{action}/{operation}/',
            controller='ckanext.wps.controllers:WpsController',
            action='{action}')
        map.connect('{action}', '/dataset/{id}/resource/{resource_id}/{action}/{operation}',
            controller='ckanext.wps.controllers:WpsController',
            action='{action}',operation='{operation}')
        return map

    # Update CKAN's config settings, see the IConfigurer plugin interface.
    def update_config(self, config):
        plugins.toolkit.add_public_directory(config, 'public')
        # Tell CKAN to use the template files in
        # ckanext/wps/templates.
        plugins.toolkit.add_template_directory(config, 'templates')
        plugins.toolkit.add_resource('public','ckanext-wps')
        self.proxy_enabled = plugins.toolkit.asbool(config.get('ckan.resource_proxy_enabled', 'False'))
    
    def setup_template_variables(self, context, data_dict):
        import ckanext.resourceproxy.plugin as proxy
        if self.proxy_enabled and not data_dict['resource']['on_same_domain']:
            plugins.toolkit.c.resource['proxy_url'] = proxy.get_proxified_resource_url(data_dict)
        else:
            plugins.toolkit.c.resource['proxy_url'] = data_dict['resource']['url']
        plugins.toolkit.c.resource['origin_url'] = data_dict['resource']['url']
    
    
    def can_preview(self, data_dict):
        format_lower = data_dict['resource']['format'].lower()
        correct_format = format_lower in self.myformat
        can_preview_from_domain = self.proxy_enabled or data_dict['resource']['on_same_domain']
        quality = 2
        if plugins.toolkit.check_ckan_version('2.1'):
            if correct_format:
                if can_preview_from_domain:
                    return {'can_preview': True, 'quality': quality}
                else:
                    return {'can_preview': False,'fixable': 'Enable resource_proxy','quality': quality}
            else:
                return {'can_preview': False, 'quality': quality}
        return correct_format and can_preview_from_domain
    
    def preview_template(self, context, data_dict):
        return 'index.html'
	
    # Tell CKAN what custom template helper functions this plugin provides,
    # see the ITemplateHelpers plugin interface.
    def get_helpers(self):
        return {'capabilities_helper': capabilities_helper,'printdir_helper':printDir()}

    def get_actions(self):
        return {
            "ckanext_wps_capabilities": wpsclient.capabilities,
            "ckanext_wps_describe": wpsclient.describe,
            "ckanext_wps_execute": wpsclient.execute#,
        }
