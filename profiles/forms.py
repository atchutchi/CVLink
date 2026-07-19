from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

from .models import Certification, Education, Experience, Profile, ProfileLanguage


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            "public_name",
            "professional_title",
            "bio",
            "location",
            "country",
            "photo",
            "specializations",
            "skills",
            "availability",
            "work_preference",
            "willing_to_relocate",
            "phone",
            "whatsapp",
            "website",
            "linkedin_url",
            "contact_visibility",
            "cv_file",
            "consent_marketing",
        )
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 5}),
            "specializations": forms.SelectMultiple(attrs={"size": 6}),
            "skills": forms.SelectMultiple(attrs={"size": 8}),
        }

    def clean_cv_file(self):
        upload = self.cleaned_data.get("cv_file")
        if not upload:
            return upload
        FileExtensionValidator(["pdf"], "O currículo deve ser um ficheiro PDF.")(upload)
        if getattr(upload, "content_type", "application/pdf") != "application/pdf":
            raise ValidationError("O currículo deve ser um ficheiro PDF.")
        if upload.size > 5 * 1024 * 1024:
            raise ValidationError("O currículo não pode exceder 5 MB.")
        return upload


class DateInput(forms.DateInput):
    input_type = "date"


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        exclude = ("profile",)
        widgets = {"start_date": DateInput(), "end_date": DateInput(), "description": forms.Textarea(attrs={"rows": 4})}


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        exclude = ("profile",)
        widgets = {"start_date": DateInput(), "end_date": DateInput(), "description": forms.Textarea(attrs={"rows": 4})}


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        exclude = ("profile",)
        widgets = {"issue_date": DateInput(), "expiry_date": DateInput()}


class ProfileLanguageForm(forms.ModelForm):
    class Meta:
        model = ProfileLanguage
        exclude = ("profile",)
