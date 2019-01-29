
from zope import schema
from zope.interface import Interface
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('collective.elasticindex')


class IElasticSettings(Interface):
    only_published = schema.Bool(
        title=_(u'Index only published content?'),
        default=True
    )
    index_security = schema.Bool(
        title=_(u'Index security?'),
        default=False
    )
    normalize_domain_name = schema.TextLine(
        title=_(u"Normalize domain name"),
        description=_(u"If specified, replace the domain name in documents "
                      u"URL with this one."),
        required=False
    )
    index_name = schema.TextLine(
        title=_(u"Index name"),
        description=_(u"Elastic-Search index name where to index and search "
                      u"for documents."),
        required=True
    )
    server_urls = schema.List(
        title=_(u"Server URLs"),
        description=_(u"URLs to contact Elastic-Search servers"),
        value_type=schema.URI(),
        required=True
    )
    public_server_urls = schema.List(
        title=_(u"Server URLs to use for the public search"),
        description=_(u"URLs for the public search to contact Elastic-Search. "
                      u"If not specified regular server URLs will be used."),
        value_type=schema.URI(),
        required=False
    )
    public_through_plone = schema.Bool(
        title=_(u"Proxy search requests through Plone and apply "
                u"security filter?"),
        description=_(u"Check this and index security if you want to "
                      u"have a private search"),
        default=False
    )

    def get_search_urls():
        pass
