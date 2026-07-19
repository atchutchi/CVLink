from django.db.models import Q

from .models import Profile


def public_profiles(params=None):
    params = params or {}
    queryset = (
        Profile.objects.filter(status=Profile.Status.APPROVED, is_public=True)
        .select_related("user")
        .prefetch_related("specializations__area__sector", "skills")
    )
    query = str(params.get("q", "")).strip()
    if query:
        queryset = queryset.filter(
            Q(public_name__icontains=query)
            | Q(professional_title__icontains=query)
            | Q(bio__icontains=query)
            | Q(location__icontains=query)
            | Q(specializations__name__icontains=query)
            | Q(skills__name__icontains=query)
        )
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
        if value:
            queryset = queryset.filter(**{field: value})
    location = str(params.get("location", "")).strip()
    if location:
        queryset = queryset.filter(location__icontains=location)
    ordering = params.get("order")
    if ordering == "name":
        return queryset.order_by("public_name").distinct()
    return queryset.order_by("-updated_at", "public_name").distinct()
