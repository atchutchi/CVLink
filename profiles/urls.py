from django.urls import path

from .views import add_section, delete_section, edit_profile, submit_profile


app_name = "profiles"

urlpatterns = [
    path("editar/", edit_profile, name="edit"),
    path("submeter/", submit_profile, name="submit"),
    path("secao/<slug:section>/adicionar/", add_section, name="section_add"),
    path("secao/<slug:section>/<int:pk>/eliminar/", delete_section, name="section_delete"),
]
