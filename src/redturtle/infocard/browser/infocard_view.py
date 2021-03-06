# -*- coding: utf-8 -*-
from plone import api
from plone.memoize.view import memoize
from Products.Five.browser import BrowserView


class InfocardView(BrowserView):
    """  """

    @property
    @memoize
    def authors(self):
        return ", ".join(sorted(self.context.infocard_authors()))

    @property
    @memoize
    def servicetypes(self):
        return ", ".join(sorted(self.context.servicetypes))

    @property
    @memoize
    def recipients(self):
        return ", ".join(sorted(self.context.recipients))

    @property
    @memoize
    def modified(self):
        return self.context.modified()

    @property
    @memoize
    def public_infos(self):
        """ Return all the infos that are public
        """
        return [info for info in self.context.order if info["publish"]]

    @property
    @memoize
    def private_infos(self):
        """ Return all the infos that are not public
        """
        return [info for info in self.context.order if not info["publish"]]

    @property
    @memoize
    def allowed_infos(self):
        """ Return all the infos that are public
        """
        if api.user.is_anonymous():
            return self.public_infos
        else:
            return self.context.order

    def getCard(self, uid):
        """ return card text """
        card = api.content.get(UID=uid)
        if card and getattr(card, "text", None):
            return card.text.raw
        return u""
