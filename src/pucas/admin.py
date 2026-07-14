from django.contrib import messages
from django.contrib.auth.admin import UserAdmin
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path

from pucas.forms import CasUserInitForm
from pucas.ldap import LDAPSearchException, LDAPSearch, init_cas_user


class CasUserAdmin(UserAdmin):
    """UserAdmin subclass with a CAS user initialization view.

    Provides a form-based interface for creating CAS user accounts by netid
    directly from the Django admin. Can be used directly or subclassed for
    further customization. See the pucas README for usage instructions.
    """

    change_list_template = "admin/pucas/user_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "cas-init/",
                self.admin_site.admin_view(self.cas_user_init),
                name="users_user_cas_init",
            ),
        ]
        return custom_urls + urls

    def cas_user_init(self, request):
        """View to initialize CAS user accounts by netid."""
        if request.method == "POST":
            form = CasUserInitForm(request.POST)
            if form.is_valid():
                netids = form.cleaned_data["netids"]
                created_list = []
                existing_list = []
                errors = []

                ldap = LDAPSearch()
                for netid in netids:
                    try:
                        _, created = init_cas_user(netid, ldap=ldap)
                        if created:
                            created_list.append(netid)
                        else:
                            existing_list.append(netid)
                    except LDAPSearchException:
                        errors.append(netid)

                if created_list:
                    self.message_user(
                        request,
                        "Created accounts: %s" % ", ".join(created_list),
                        messages.SUCCESS,
                    )
                if existing_list:
                    self.message_user(
                        request,
                        "Already exists: %s" % ", ".join(existing_list),
                        messages.INFO,
                    )
                if errors:
                    self.message_user(
                        request,
                        "NetIDs not found in LDAP: %s" % ", ".join(errors),
                        messages.ERROR,
                    )

                return redirect("..")
        else:
            form = CasUserInitForm()

        context = dict(
            self.admin_site.each_context(request),
            form=form,
            opts=self.model._meta,
            title="Add CAS Users",
        )
        return TemplateResponse(
            request,
            "admin/pucas/cas_user_init.html",
            context,
        )
