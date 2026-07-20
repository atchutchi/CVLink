"""Query helpers for the public directory.

Search intentionally operates on the approved payload for profiles with pending
changes.  This prevents an unreviewed edit from leaking into the public index,
while still allowing the relational taxonomy fields to be used for profiles
that have not yet received their first snapshot.
"""

import re
import unicodedata
from datetime import date

from django.db.models import Case, IntegerField, Q, Value, When
from django.utils.text import slugify

from .models import Profile


_SYNONYMS = {
    "informatico": ("informatico", "tecnico de informatica", "suporte tecnico", "administrador de sistemas", "ti"),
    "programador": ("programador", "desenvolvedor", "developer", "software engineer"),
    "desenvolvedor": ("programador", "desenvolvedor", "developer", "software engineer"),
    "comunicacao": ("comunicacao", "comunicacao institucional", "relacoes publicas", "comunicacao social"),
    "rh": ("rh", "recursos humanos"),
    "recursos": ("recursos", "recursos humanos"),
    "ti": ("ti", "tecnologia da informacao", "informatica"),
}


def _normalise(value):
    value = unicodedata.normalize("NFKD", str(value or ""))
    return "".join(char for char in value if not unicodedata.combining(char)).casefold()


def _snapshot_text(snapshot):
    if not snapshot:
        return ""
    values = [snapshot.get(key, "") for key in ("public_name", "professional_title", "bio", "availability_label", "work_preference_label")]
    if snapshot.get("location_is_public", False):
        values.append(snapshot.get("location", ""))
        values.append(snapshot.get("country", ""))
    for key in ("skills", "specializations", "areas", "sectors"):
        values.extend(snapshot.get(key, []))
    for key in ("experiences", "education", "certifications", "languages"):
        for item in snapshot.get(key, []):
            values.extend(item.values() if isinstance(item, dict) else [item])
    return " ".join(_normalise(value) for value in values)


def _profile_search_data(profile):
    """Return public searchable text and a relevance score for one profile."""
    payload = profile.published_snapshot or {}
    if payload:
        text = _snapshot_text(payload)
        title = _normalise(payload.get("professional_title"))
        location = _normalise(payload.get("location")) if payload.get("location_is_public", False) else ""
    else:
        values = [profile.public_name, profile.professional_title, profile.bio, profile.get_availability_display(), profile.get_work_preference_display()]
        if profile.location_is_public:
            values.extend((profile.location, profile.country))
        values.extend(profile.specializations.values_list("name", flat=True))
        values.extend(profile.specializations.values_list("area__name", flat=True))
        values.extend(profile.specializations.values_list("area__sector__name", flat=True))
        values.extend(profile.skills.values_list("name", flat=True))
        for experience in profile.experiences.all():
            values.extend((experience.title, experience.organization, experience.description))
        for education in profile.education_entries.all():
            values.extend((education.qualification, education.institution, education.field_of_study))
        for certification in profile.certifications.all():
            values.extend((certification.name, certification.issuer))
        values.extend(language.name for language in profile.languages.all())
        text = " ".join(_normalise(value) for value in values)
        title = _normalise(profile.professional_title)
        location = _normalise(profile.location) if profile.location_is_public else ""
    return text, title, location


def _query_matches(text, query):
    tokens = [_normalise(token) for token in re.findall(r"\w+", query, flags=re.UNICODE) if token.strip()]
    return all(
        any(option in text for option in _SYNONYMS.get(token, (token,)) + _SYNONYMS.get(token.rstrip("s"), (token.rstrip("s"),)))
        for token in tokens
    )


def _param(params, *names):
    for name in names:
        value = str(params.get(name, "")).strip()
        if value:
            return value
    return ""


def public_profiles(params=None):
    params = params or {}
    queryset = (
        Profile.objects.filter(
            Q(status=Profile.Status.APPROVED) | Q(status=Profile.Status.CHANGES_PENDING),
            is_public=True,
        )
        .select_related("user")
        .prefetch_related(
            "specializations__area__sector",
            "skills",
            "experiences",
            "education_entries",
            "certifications",
            "languages",
        )
    )

    query = str(params.get("q", "")).strip()
    relevance = {}
    if query:
        matches = []
        for profile in queryset:
            text, title, _ = _profile_search_data(profile)
            if _query_matches(text, query):
                matches.append(profile.pk)
                score = 0
                normalised_query = _normalise(query)
                if normalised_query and normalised_query in title:
                    score += 100
                score += sum(10 for token in re.findall(r"\w+", query, flags=re.UNICODE) if _normalise(token) in title)
                relevance[profile.pk] = score
        queryset = queryset.filter(pk__in=matches)

    filters = {
        "sector": "specializations__area__sector__slug",
        "area": "specializations__area__slug",
        "specialization": "specializations__slug",
        "skill": "skills__slug",
        "availability": "availability",
        "work_preference": "work_preference",
    }
    for parameter, field in filters.items():
        value = str(params.get(parameter, "")).strip()
        if not value:
            continue
        if parameter in {"availability", "work_preference"}:
            queryset = queryset.filter(
                (Q(published_snapshot={}) & Q(**{field: value}))
                | Q(**{f"published_snapshot__{parameter}": value})
            )
        else:
            matching_ids = []
            for profile in queryset:
                payload = profile.published_snapshot or {}
                if payload:
                    names = payload.get({
                        "sector": "sectors",
                        "area": "areas",
                        "specialization": "specializations",
                        "skill": "skills",
                    }[parameter], [])
                    if any(slugify(name) == value for name in names):
                        matching_ids.append(profile.pk)
                else:
                    relation = {
                        "sector": profile.specializations.filter(area__sector__slug=value),
                        "area": profile.specializations.filter(area__slug=value),
                        "specialization": profile.specializations.filter(slug=value),
                        "skill": profile.skills.filter(slug=value),
                    }[parameter]
                    if relation.exists():
                        matching_ids.append(profile.pk)
            queryset = queryset.filter(pk__in=matching_ids)

    location = _param(params, "location", "cidade", "city")
    if location:
        queryset = queryset.filter(
            (Q(published_snapshot={}) & Q(location_is_public=True) & Q(location__icontains=location))
            | (Q(published_snapshot__location_is_public=True) & Q(published_snapshot__location__icontains=location))
        )

    country = _param(params, "country", "pais")
    if country:
        matching_ids = []
        for profile in queryset:
            payload = profile.published_snapshot or {}
            if payload:
                if not payload.get("location_is_public", False):
                    continue
                candidate = payload.get("country", "")
            elif profile.location_is_public:
                candidate = profile.country
            else:
                candidate = ""
            if _normalise(country) in _normalise(candidate):
                matching_ids.append(profile.pk)
        queryset = queryset.filter(pk__in=matching_ids)

    language = _param(params, "language", "idioma")
    if language:
        matching_ids = []
        for profile in queryset:
            payload = profile.published_snapshot or {}
            names = [item.get("name", "") for item in payload.get("languages", [])] if payload else profile.languages.values_list("name", flat=True)
            if any(slugify(name) == slugify(language) or _normalise(language) in _normalise(name) for name in names):
                matching_ids.append(profile.pk)
        queryset = queryset.filter(pk__in=matching_ids)

    minimum_years = _param(params, "experience", "years_experience", "anos_experiencia")
    if minimum_years.isdigit():
        threshold = int(minimum_years)
        matching_ids = []
        for profile in queryset:
            payload = profile.published_snapshot or {}
            records = payload.get("experiences", []) if payload else profile.experiences.all()
            total_days = 0
            for record in records:
                start = record.get("start_date") if isinstance(record, dict) else record.start_date
                end = record.get("end_date") if isinstance(record, dict) else record.end_date
                if not start:
                    continue
                start_date = date.fromisoformat(start) if isinstance(start, str) else start
                end_date = date.fromisoformat(end) if isinstance(end, str) and end else (end or date.today())
                total_days += max(0, (end_date - start_date).days)
            if total_days >= threshold * 365:
                matching_ids.append(profile.pk)
        queryset = queryset.filter(pk__in=matching_ids)

    if _param(params, "cv", "cv_available", "curriculo") in {"1", "true", "yes", "sim"}:
        queryset = queryset.filter(cv_file__isnull=False).exclude(cv_file="").exclude(cv_visibility=Profile.CVVisibility.PRIVATE)

    ordering = str(params.get("order", "relevance"))
    if query and ordering in {"relevance", ""} and relevance:
        whens = [When(pk=pk, then=Value(score)) for pk, score in relevance.items()]
        queryset = queryset.annotate(_relevance=Case(*whens, default=Value(0), output_field=IntegerField())).order_by("-_relevance", "-updated_at", "public_name")
    elif ordering in {"name", "name_asc"}:
        queryset = queryset.order_by("public_name", "pk")
    elif ordering == "name_desc":
        queryset = queryset.order_by("-public_name", "-pk")
    elif ordering in {"experience", "most_experience"}:
        queryset = queryset.order_by("-experiences__start_date", "public_name")
    else:
        queryset = queryset.order_by("-updated_at", "public_name", "pk")
    return queryset.distinct()
