from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from taxonomy.models import Area, Sector, Skill, Specialization

from .models import Profile
from .selectors import public_profiles


def search(request):
    paginator = Paginator(public_profiles(request.GET), 12)
    page = paginator.get_page(request.GET.get("page"))
    filter_params = request.GET.copy()
    filter_params.pop("page", None)
    context = {
        "page_obj": page,
        "filter_query": filter_params.urlencode(),
        "sectors": Sector.objects.filter(is_active=True),
        "areas": Area.objects.filter(is_active=True).select_related("sector"),
        "specializations": Specialization.objects.filter(is_active=True).select_related("area"),
        "skills": Skill.objects.filter(is_active=True),
        "availability_choices": Profile.Availability.choices,
        "work_preference_choices": Profile.WorkPreference.choices,
    }
    return render(request, "profiles/search.html", context)


def public_profile(request, slug):
    profile = get_object_or_404(
        public_profiles(),
        slug=slug,
    )
    return render(request, "profiles/public_detail.html", {"profile": profile})
