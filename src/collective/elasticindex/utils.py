
import pyes
import urlparse

from collective.elasticindex.interfaces import IElasticSettings

ANALYZED_STRING_MAPPING = {
    'index'    : 'analyzed',
    'type'     : 'string', 
    'store'    : 'yes', 
    'analyzer' : 'standard'
}

STRING_MAPPING = {
    'index'    : 'not_analyzed',
    'type'     : 'string', 
    'store'    : 'yes', 
}

DATE_MAPPING = {
    'index' : 'not_analyzed',
    'type'  : 'date',
    'store' : 'no'
}

DOCUMENT_MAPPING = {
    '_index' : {
        'enabled' : True
    },
    '_id' : {
        'index' : 'not_analyzed',
        'store' : 'yes'
    },

    'site'    : STRING_MAPPING,

    'url'     : ANALYZED_STRING_MAPPING,
    'author'  : ANALYZED_STRING_MAPPING,
    'title'   : ANALYZED_STRING_MAPPING,
    'subject' : ANALYZED_STRING_MAPPING,
    'content' : ANALYZED_STRING_MAPPING,
    
    'created'  : DATE_MAPPING,
    'modified' : DATE_MAPPING 
}

def parse_url(url):
    info = urlparse.urlparse(url)
    if ':' in info.netloc:
        url, port = info.netloc.split(':', 1)
    else:
        port = 80
        if info.scheme == 'https':
            port = 443
        url = info.netloc
    return 'http', url, int(port)


def connect(urls):
    try:
        return pyes.ES(map(parse_url, urls))
    except:
        raise ValueError('Cannot connect to servers')


def create_index(settings):
    connection = connect(settings.server_urls)
    connection.indices.create_index_if_missing(settings.index_name)
    connection.indices.put_mapping(
        'document', {'properties' : DOCUMENT_MAPPING}, [settings.index_name])
