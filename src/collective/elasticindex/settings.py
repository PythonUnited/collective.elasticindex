
from Acquisition import aq_base
from Products.CMFCore.interfaces import IPropertiesTool
from collective.elasticindex.interfaces import IElasticSettings
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone import api


class SettingsAdapter(object):

    def __init__(self, context):
        self._id = context.getId()

        registry = getUtility(IRegistry)
        records = registry.forInterface(IElasticSettings)
        self._activated = bool(records)

    @property
    def activated(self):
        return self._activated

    def get_search_urls(self):
        return map(lambda u: '/'.join((u, self.index_name, '_search')),
            self.public_server_urls or self.server_urls)

    @property
    def only_published(self):
        return api.portal.get_registry_record(
            'collective.elasticindex.interfaces.IElasticSettings.only_published'
        )

    @property
    def index_security(self):
        return api.portal.get_registry_record(
            'collective.elasticindex.interfaces.IElasticSettings.index_security'
        )

    @property
    def index_name(self):
        return api.portal.get_registry_record(
            'collective.elasticindex.interfaces.IElasticSettings.index_name'
        )

    @property
    def normalize_domain_name(self):
        return api.portal.get_registry_record(
            'collective.elasticindex.interfaces.IElasticSettings.'
            'normalize_domain_name'
        )

    @property
    def server_urls(self):
        return api.portal.get_registry_record(
            'collective.elasticindex.interfaces.IElasticSettings.server_urls'
        )

    @property
    def public_server_urls(self):
        return api.portal.get_registry_record(
            'collective.elasticindex.interfaces.IElasticSettings.'
            'public_server_urls'
        )

    @property
    def public_through_plone(self):
        return api.portal.get_registry_record(
            'collective.elasticindex.interfaces.IElasticSettings.public_through_plone'
        )
