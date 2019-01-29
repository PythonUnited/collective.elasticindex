
from Products.statusmessages.interfaces import IStatusMessage
# from plone.app.controlpanel.form import ControlPanelForm
# from zope.formlib import form
from zope.i18nmessageid import MessageFactory
from zope import schema

from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.directives import form
from z3c.form import field, button
from collective.elasticindex.interfaces import IElasticSettings
from collective.elasticindex.changes import changes
from collective.elasticindex.utils import create_index, delete_index


_ = MessageFactory('collective.elasticindex')


class SettingsEditForm(RegistryEditForm):
    schema = IElasticSettings
    label = u"Elasticsearch settings"

    fields = field.Fields(IElasticSettings)

    @button.buttonAndHandler(_(u"Save"), name='save')
    def handleSave(self, action):
        super(SettingsEditForm, self).handleSave(self, action)

    @button.buttonAndHandler(_(u"Cancel"), name='cancel')
    def handleCancel(self, action):
        super(SettingsEditForm, self).handleCancel(self, action)

    @button.buttonAndHandler(_(u"Create index"), name='create_index')
    def handle_create_index(self, action):
        create_index(IElasticSettings(self.context))
        IStatusMessage(self.request).add("Index created.")

    @button.buttonAndHandler(_(u"Delete index"), name='delete_index')
    def handle_delete_index(self, action):
        delete_index(IElasticSettings(self.context))
        IStatusMessage(self.request).add("Index deleted.")

    @button.buttonAndHandler(_(u"Import site content"), name='import_content')
    def handle_import_content(self, action):
        changes.verify_and_index_container(self.context)
        IStatusMessage(self.request).add("Index refreshed.")


class SettingsView(ControlPanelFormWrapper):
    form = SettingsEditForm


