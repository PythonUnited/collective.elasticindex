import re
import zope.interface


class ISuggester(zope.interface.Interface):
    """ Interface for suggester """


class Suggester(object):
    zope.interface.implements(ISuggester)

    def __init__(self, context):
        self.context = context

    def terms(self):
        sentences = re.compile(r'([A-Z][^\.!?]*[\.!?])', re.M)

        suggested_terms = [self.title]
        suggested_terms += sentences.findall(self.description)
        suggested_terms += list(self.subject)

        return map(
            lambda term: term.strip(), suggested_terms
        )

    @property
    def title(self):
        return self.context.Title()

    @property
    def description(self):
        return self.context.Description()

    @property
    def subject(self):
        return self.context.Subject()
