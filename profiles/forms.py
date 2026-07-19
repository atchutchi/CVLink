from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

from .models import Certification, Education, Experience, Profile, ProfileLanguage


class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cv_visibility"].required = False

    class Meta:
        model = Profile
        fields = (
            "public_name",
            "professional_title",
            "bio",
            "location",
            "location_is_public",
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
            "cv_visibility",
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
        if upload.size > 10 * 1024 * 1024:
            raise ValidationError("O currículo não pode exceder 10 MB.")
        return upload

    def clean_cv_visibility(self):
        return self.cleaned_data.get("cv_visibility") or self.instance.cv_visibility


class DateInput(forms.DateInput):
    input_type = "date"


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        exclude = ("profile",)
        widgets = {"start_date": DateInput(), "end_date": DateInput(), "description": forms.Textarea(attrs={"rows": 4})}

    def clean(self):
        cleaned = super().clean()
        start_date = cleaned.get("start_date")
        end_date = cleaned.get("end_date")
        if start_date and end_date and end_date < start_date:
            self.add_error("end_date", "A data de fim não pode ser anterior à data de início.")
        if cleaned.get("is_current") and end_date:
            self.add_error("end_date", "Um cargo actual não pode ter data de fim.")
        return cleaned


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        exclude = ("profile",)
        widgets = {"start_date": DateInput(), "end_date": DateInput(), "description": forms.Textarea(attrs={"rows": 4})}

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("start_date") and cleaned.get("end_date") and cleaned["end_date"] < cleaned["start_date"]:
            self.add_error("end_date", "A data de fim não pode ser anterior à data de início.")
        return cleaned


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        exclude = ("profile",)
        widgets = {"issue_date": DateInput(), "expiry_date": DateInput()}

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("issue_date") and cleaned.get("expiry_date") and cleaned["expiry_date"] < cleaned["issue_date"]:
            self.add_error("expiry_date", "A validade não pode ser anterior à emissão.")
        return cleaned


class ProfileLanguageForm(forms.ModelForm):
    class Meta:
        model = ProfileLanguage
        exclude = ("profile",)
