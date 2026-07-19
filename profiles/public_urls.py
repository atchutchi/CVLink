from django.urls import path

from .public_views import public_profile, search


urlpatterns = [
    path("pesquisar/", search, name="search"),
    path("profissionais/<slug:slug>/", public_profile, name="public-profile"),
]
