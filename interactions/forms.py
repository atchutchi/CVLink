from django import forms

from .models import ContactRequest, Favorite, Report, SavedSearch


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


class FavoriteUpdateForm(forms.ModelForm):
    tags = forms.CharField(required=False, max_length=500)

    class Meta:
        model = Favorite
        fields = ("status", "notes")
        widgets = {"notes": forms.Textarea(attrs={"rows": 4})}


class SavedSearchForm(forms.ModelForm):
    class Meta:
        model = SavedSearch
        fields = ("name",)
