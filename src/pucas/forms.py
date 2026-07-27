from django import forms
from django.core.validators import RegexValidator


netid_validator = RegexValidator(
    r"^[a-zA-Z0-9]+$",
    "NetIDs may only contain alphanumeric characters.",
)


class CasUserInitForm(forms.Form):
    """Form to initialize one or more CAS user accounts by netid."""

    netids = forms.CharField(
        label="NetIDs",
        help_text="Enter one or more Princeton NetIDs, separated by spaces or newlines.",
        widget=forms.Textarea(attrs={"rows": 4}),
    )

    def clean_netids(self):
        netids = self.cleaned_data["netids"].split()
        for netid in netids:
            netid_validator(netid)
        return netids
