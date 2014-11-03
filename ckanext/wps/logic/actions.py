from ckanext.wps import settings
from logging import getLogger
import ckan.plugins.toolkit as toolkit
from pylons import config
from ckan.lib.base import abort

log = getLogger(__name__)

@toolkit.side_effect_free
def capabilities(context, data_dict):
    """Run GetCapabilities request from a WPS ressource.
    :param id: the WPS resource
    :type id: string
    :returns: the available capabilities for this resource
    :rtype: dict or None
    """
    res=toolkit.get_action("resource_show")(context=context,
                                            data_dict=data_dict)
    import urllib2
    import owslib.wps
    response = urllib2.urlopen(res['url'])
    tmp=response.read()
    wps=owslib.wps.WebProcessingService(str(res['url']))
    #wps.getcapabilities(tmp)
    wps.processes1=wps.processes#[:len(wps.processes)/2]
    final_res={
        "identification":{},
        "provider":{},
        "processes":[]      
    }
    for i in dir(wps.identification):
        if i[0]!="_":
            final_res["identification"][i]=wps.identification.__getattribute__(i)
    final_res["provider"]["name"]=wps.provider.name
    final_res["provider"]["url"]=wps.provider.url
    final_res["provider"]["contact"]={}
    for i in dir(wps.provider.contact):
        if i[0]!="_":
            final_res["provider"]["contact"][i]=wps.provider.contact.__getattribute__(i)
    
    for i in dir(wps.identification):
        if i[0]!="_":
            final_res["identification"][i]=wps.identification.__getattribute__(i)
    limit=100000
    offset=0
    if data_dict.has_key("limit"):
        limit=int(data_dict["limit"])
    if data_dict.has_key("offset"):
        offset=int(data_dict["offset"])
    cnt=0
    for p in wps.processes:
        if cnt >= offset and cnt < offset+limit:
            final_res["processes"]+=[{
                "identifier": p.identifier,
                "title": p.title,
                "abstract": p.abstract,
                "processVersion": p.processVersion,
                "statusSupported": p.statusSupported,
                "storeSupported": p.storeSupported,
            }]
        cnt+=1

    wps.provider.contact.keys=dir(wps.provider.contact)
    return final_res

@toolkit.side_effect_free
def describe(context, data_dict):
    """Run DescribeProcess request from a WPS ressource.
    :param id: the WPS resource
    :type id: string
    :param p: the identifier (or identifiers list separated by ',') of the service to run
    :type p: string
    :returns: the capabilities for this resource
    :rtype: dict or None
    """
    res=toolkit.get_action("resource_show")(context=context,
                                            data_dict=data_dict)
    import urllib2
    import owslib.wps
    response = urllib2.urlopen(res['url'])
    tmp=response.read()
    wps=owslib.wps.WebProcessingService(str(res['url']))
    #wps.getcapabilities(tmp)
    for i in wps.operations:
        if i.name=="DescribeProcess":
            wps1=owslib.wps.WebProcessingService(i.methods["Post"]["url"])
            break
    if data_dict["p"].count(",")>0:
        final_res=[]
        for i in data_dict["p"].split(","):
            final_res+=[describeAProcess(wps1,i)]
    else:
        if data_dict["p"].count("all")>0:
            final_res=[]
            for i in wps.processes[:len(wps.processes)/2]:
                final_res+=[describeAProcess(wps1,i.identifier)]
        else:
            final_res=describeAProcess(wps1,data_dict["p"])
    return final_res

@toolkit.side_effect_free
def execute(context, data_dict):
    """Run Execute request from a WPS ressource.
    :param id: the WPS resource
    :type id: string
    :returns: the execute outputs
    :rtype: dict or None
    """
    #toolkit.check_access("ckanext_deadoralive_get", context, data_dict)
    # TODO: Validation.
    #resource_id = data_dict["resource_id"]
    res = toolkit.get_action("resource_show")(context=context,
                                            data_dict=data_dict)
    log.info(res)
    import urllib2
    import owslib.wps
    from owslib.etree import etree
    from owslib.ows import DEFAULT_OWS_NAMESPACE
    from owslib.util import (testXMLValue, build_get_url, dump, getTypedValue,
        getNamespace, nspath, openURL, nspath_eval)
    from owslib.namespaces import Namespaces
    
    n = Namespaces()
    
    def get_namespaces():
        ns = n.get_namespaces(["ogc","wfs","wps","gml","xsi","xlink"])
        ns[None] = n.get_namespace("wps")
        ns["ows"] = DEFAULT_OWS_NAMESPACE
        return ns

    namespaces = get_namespaces()

    class CKANStaticFeatureCollection(owslib.wps.WFSFeatureCollection):
        def __init__(self,url):
            self.url = url
        def getXml(self):
            root = etree.Element(nspath_eval('wps:Reference', namespaces), attrib = { nspath_eval("xlink:href",namespaces) : self.url, "mimeType" : "text/xml"} )
            return root

    class CKANStaticValues(owslib.wps.WFSFeatureCollection):
        def __init__(self,url):
            self.url = url
        def getXml(self):
            root = etree.Element(nspath_eval('wps:Reference', namespaces), attrib = { nspath_eval("xlink:href",namespaces) : self.url, "mimeType" : "text/xml"} )
            return root
        
    response = urllib2.urlopen(res['url'])
    tmp=response.read()
    wps=owslib.wps.WebProcessingService(str(res['url']))
    #wps.getcapabilities(tmp)
    for i in wps.operations:
        if i.name=="Execute":
            wps1=owslib.wps.WebProcessingService(i.methods["Post"]["url"],verbose=True)
            break
    inputs=[]
    j=0
    for i in data_dict.keys():
        if i[:3]=="ir_":
            res=toolkit.get_action("resource_show")(context=context,
                                                    data_dict={"id": data_dict[i]})
            inputs+=[(i.replace("ir_",""), CKANStaticFeatureCollection(res['url']))]
        if i[:2]=="i_":
            inputs+=[(i.replace("i_",""), str(data_dict[i]))]
        j+=1
    try:
        final_res=wps1.execute(data_dict["p"],inputs,output=[(data_dict["out"],True)])
        if data_dict.has_key("async") and data_dict["async"]=="true":
            final_res={"reference": final_res.statusLocation,"status": final_res.statusMessage}
        else:
            from owslib.wps import monitorExecution
            monitorExecution(final_res)
            final_res={"reference": final_res.processOutputs[0].reference,"status": final_res.statusMessage,"keys":res.keys()}
    except Exception,e:
        final_res={"error": str(e),"response":"None"}
        return final_res
    try:
        lpkg=config['ckanext-wps.target_dataset']
        if data_dict.has_key("pkg"):
            log.info("ok");
            pkg=toolkit.get_action("package_show")(context=context,
                                                    data_dict={"id": data_dict["pkg"]})
            lpkg=pkg["id"]
        resource = toolkit.get_action('resource_create')(context=context,data_dict={
            "package_id": lpkg,
            "url": final_res["reference"],
            "description": final_res["status"],
            "name": "WPS Result: "+data_dict["p"]+" ",
            "mimetype": "application/json",
            "format": "geojson"
        })
        final_res["ckan_resource"]=resource["id"]
    except Exception,e:
        final_res["ckan_error"]=str(e)
    final_res["tmp"]={
        "package_id": lpkg,
        "url": final_res["reference"],
        "description": final_res["status"],
        "name": "WPS Result: "+data_dict["p"]+" ",
        "mimetype": "application/json",
        "format": "geojson"
    }
    
    return final_res

    
def describeAProcess(wps1,id):
    process=wps1.describeprocess(id)
    final_res={
        "identifier": process.identifier,
        "title": process.title,
        "abstract": process.abstract
    }
    final_res["dataInputs"]=[]
    for i in process.dataInputs:
        tmp={
            "identifier": i.identifier,
            "title": i.title,
            "abstract": i.abstract,
            "dataType": i.dataType,
            "minoccurs": i.minOccurs,
            "maxoccurs": i.maxOccurs
        }
        if i.dataType=="ComplexData":
            tmp["mimeType"]=i.defaultValue.mimeType
            tmp["encoding"]=i.defaultValue.encoding
            tmp["schema"]=i.defaultValue.schema
            for val in i.allowedValues:
                if not(tmp.has_key("allowedvalues")):
                    tmp["allowedvalues"]=[]
                tmp["allowedvalues"]+=[{
                    "mimeType": val.mimeType,
                    "encoding": val.encoding,
                    "schema": val.schema
                }]
            for val in i.supportedValues:
                if not(tmp.has_key("supportedvalues")):
                    tmp["supportedvalues"]=[]
                tmp["supportedvalues"]+=[{
                    "mimeType": val.mimeType,
                    "encoding": val.encoding,
                    "schema": val.schema
                }]
            
        final_res["dataInputs"]+=[tmp]
    final_res["processOutputs"]=[]
    for i in process.processOutputs:
        tmp={
            "identifier": i.identifier,
            "title": i.title,
            "abstract": i.abstract,
            "dataType": i.dataType
        }
        if i.dataType=="ComplexData":
            tmp["mimeType"]=i.defaultValue.mimeType
            tmp["encoding"]=i.defaultValue.encoding
            tmp["schema"]=i.defaultValue.schema
            for val in i.allowedValues:
                if not(tmp.has_key("allowedvalues")):
                    tmp["allowedvalues"]=[]
                tmp["allowedvalues"]+=[{
                    "mimeType": val.mimeType,
                    "encoding": val.encoding,
                    "schema": val.schema
                }]
            for val in i.supportedValues:
                if not(tmp.has_key("supportedvalues")):
                    tmp["supportedvalues"]=[]
                tmp["supportedvalues"]+=[{
                    "mimeType": val.mimeType,
                    "encoding": val.encoding,
                    "schema": val.schema
                }]
            
        final_res["processOutputs"]+=[tmp]
    return final_res
