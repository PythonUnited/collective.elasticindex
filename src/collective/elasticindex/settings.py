
from Acquisition import aq_base
from Products.CMFCore.interfaces import IPropertiesTool
from zope.component import getUtility


class EmptySettings(object):
    index_name = None
    server_urls = []


class SettingsAdapter(object):

    def __init__(self, context):
        self._id = context.getId()
        properties = getUtility(IPropertiesTool)
        self._activated = hasattr(
            aq_base(properties),
            'elasticindex_properties')
        if self._activated:
            self._properties = properties.elasticindex_properties
        else:
            self._properties = EmptySettings()

    @property
    def activated(self):
        return self._activated

    @apply
    def index_name():

        def getter(self):
            if self._properties.index_name:
                return self._properties.index_name
            return self._id

        def setter(self, value):
            self._properties.index_name = value
            return value

        return property(getter, setter)

    @apply
    def server_urls():

        def getter(self):
            return self._properties.server_urls

        def setter(self, value):
            self._properties.server_urls = tuple(value)
            return self._properties.server_urls

        return property(getter, setter)