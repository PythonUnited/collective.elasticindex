from plone import api
import pyes
import urlparse

TEXT_MAPPING = {
    'type': 'text',
}

STORED_TEXT_MAPPING = {
    'type': 'text',
    'store': True,
}

KEYWORD_MAPPING = {
    'type': 'keyword',
}

STORED_KEYWORD_MAPPING = {
    'type': 'keyword',
    'store': True
}

DATE_MAPPING = {
    'type': 'date',
}

INT_MAPPING = {
    'type': 'integer',
}

SUGGEST_MAPPING = {
    'type': 'completion',
    'max_input_length': 80
}

DOCUMENT_MAPPING = {
    # Stored
    'title': STORED_TEXT_MAPPING,
    'subject': STORED_TEXT_MAPPING,
    'description': STORED_TEXT_MAPPING,
    'content': STORED_TEXT_MAPPING,
    'author': STORED_TEXT_MAPPING,
    'contributors': STORED_TEXT_MAPPING,

    # Not analyzed
    'url': STORED_KEYWORD_MAPPING,
    'metaType': STORED_KEYWORD_MAPPING,

    # Not stored
    'created': DATE_MAPPING,
    'modified': DATE_MAPPING,
    'publishedYear': INT_MAPPING,
    'sortableTitle': KEYWORD_MAPPING,
    'authorizedUsers': KEYWORD_MAPPING,

    'suggest': SUGGEST_MAPPING,
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
    language_settings = None
    if api.portal.get_default_language() == 'nl':
        language_settings = {
            'settings': {
                'analysis': {
                    'filter': {
                        'dutch_stop': {
                            'stopwords': '_dutch_',
                            'type': 'stop'
                        },
                        'dutch_stemmer': {
                            'type': 'stemmer',
                            'language': 'dutch'
                        }
                    },
                    'analyzer': {
                        'dutch': {
                            'filter': [
                                'lowercase',
                                'dutch_stop',
                                'dutch_stemmer'
                            ],
                           'tokenizer': 'standard'
                        }
                    }
                }
            }
        }

    connection = connect(settings.server_urls)
    connection.indices.create_index_if_missing(settings.index_name, language_settings)
    connection.indices.put_mapping(
        'document', {'properties': DOCUMENT_MAPPING}, [settings.index_name])


def delete_index(settings):
    connection = connect(settings.server_urls)
    connection.indices.delete_index_if_exists(settings.index_name)
