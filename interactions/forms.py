from django import forms

from .models import ContactRequest, Report


class ContactRequestForm(forms.ModelForm):
    class Meta:
        model = ContactRequest
        fields = ("subject", "message")
        widgets = {"message": forms.Textarea(attrs={"rows": 7})}


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ("reason", "description")
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}

