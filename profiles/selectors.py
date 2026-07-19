from django.db.models import Q

from .models import Profile


def public_profiles(params=None):
    params = params or {}
    queryset = (
        Profile.objects.filter(
            Q(status=Profile.Status.APPROVED) | Q(status=Profile.Status.CHANGES_PENDING),
            is_public=True,
        )
        .select_related("user")
        .prefetch_related("specializations__area__sector", "skills")
    )
    query = str(params.get("q", "")).strip()
    if query:
        current_fields = (
            Q(public_name__icontains=query)
            | Q(professional_title__icontains=query)
            | Q(bio__icontains=query)
            | Q(location__icontains=query)
            | Q(specializations__name__icontains=query)
            | Q(skills__name__icontains=query)
        )
        published_fields = (
            Q(published_snapshot__public_name__icontains=query)
            | Q(published_snapshot__professional_title__icontains=query)
            | Q(published_snapshot__bio__icontains=query)
            | Q(published_snapshot__location__icontains=query)
        )
        queryset = queryset.filter(
            (Q(published_snapshot={}) & current_fields)
            | (~Q(published_snapshot={}) & published_fields)
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
            if parameter in {"availability", "work_preference"}:
                queryset = queryset.filter(
                    (Q(published_snapshot={}) & Q(**{field: value}))
                    | Q(**{f"published_snapshot__{parameter}": value})
                )
            else:
                queryset = queryset.filter(published_snapshot={}, **{field: value})
    location = str(params.get("location", "")).strip()
    if location:
        queryset = queryset.filter(
            (Q(published_snapshot={}) & Q(location__icontains=location))
            | Q(published_snapshot__location__icontains=location)
        )
    ordering = params.get("order")
    if ordering == "name":
        return queryset.order_by("public_name").distinct()
    return queryset.order_by("-updated_at", "public_name").distinct()
