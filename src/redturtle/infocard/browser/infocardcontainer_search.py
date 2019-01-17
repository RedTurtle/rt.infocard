# -*- coding: utf-8 -*-
from plone import api
from plone.directives import form
from plone.z3cform.layout import wrap_form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from redturtle.infocard import _
from z3c.form import button
from zope import schema
from zope.interface import Invalid
from zope.interface import invariant


class IInfocardContainerSearchForm(form.Schema):
    """ Define form fields """

    text = schema.TextLine(
        title=_("label_search_text", u"Search text"), required=False
    )
    servicetype = schema.Choice(
        title=_("label_servicetype", u"Service type"),
        vocabulary="redturtle.infocard.infocardcontainer.servicetypes",
        required=False,
    )
    recipient = schema.Choice(
        title=_("label_for_who_is_it", u"For who is it?"),
        vocabulary="redturtle.infocard.infocardcontainer.recipients",
        required=False,
    )

    @invariant
    def at_least_one(data):
        if data.servicetype or data.recipient or data.text:
            return
        raise Invalid(
            _(
                "label_at_least_one_search_parameter",
                u"You should specify at least one search parameter",
            )
        )


class InfocardContainerSearchForm(form.SchemaForm):

    ignoreContext = True
    schema = IInfocardContainerSearchForm
    searching = False

    table_fields = [
        {"id": "title", "label": _("title")},
        {"id": "description", "label": _("description")},
        {
            "id": "servicetypes",
            "label": _("label_servicetypes", u"Service types"),
        },
        {
            "id": "recipients",
            "label": _("label_for_who_is_it", u"For who is it?"),
        },
    ]

    def _init_(self, context, request):
        self.context = context
        self.request = request

    def accept_infocard(self, infocard, data):
        """ Given the data in the parameters filter the infocard
        """
        if data.get("servicetype"):
            if not data.get("servicetype") in infocard.servicetypes:
                return False
        if data.get("recipient"):
            if not data.get("recipient") in infocard.recipients:
                return False
        if data.get("text"):
            infocard_view = api.content.get_view(
                "view", infocard, self.request
            )  # noqa
            if not data.get("text").lower() in infocard_view.searched_text:
                return False
        return True

    def search_results(self, data):
        """
        """
        infocards = self.context.listFolderContents(
            {"portal_type": "infocard"}
        )
        results = []
        for infocard in infocards:
            if self.accept_infocard(infocard, data):
                infocard_view = api.content.get_view(
                    "view", infocard, self.request
                )  # noqa
                results.append(
                    {
                        "review_state": api.content.get_state(infocard),
                        "url": infocard.absolute_url,
                        "title": infocard.title,
                        "description": infocard.description,
                        "servicetypes": infocard_view.servicetypes,
                        "recipients": infocard_view.recipients,
                    }
                )
        sorted(results, key=lambda x: x["title"])
        return results

    @button.buttonAndHandler(_("label_search", u"Search"))
    def handleSearch(self, action):
        self.searching = True
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            self.results = []
            return
        self.results = self.search_results(data)

    @button.buttonAndHandler(_("label_cancel", u"Cancel"))
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """


infocardcontainersearchform_view = wrap_form(
    InfocardContainerSearchForm,
    index=ViewPageTemplateFile('templates/infocardcontainer_search.pt')
)