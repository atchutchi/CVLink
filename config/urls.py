from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("", include("profiles.public_urls")),
    path("", include("taxonomy.urls")),
    path("", include("core.urls")),
    path("conta/", include("accounts.urls")),
    path("perfil/", include("profiles.urls")),
    path("administracao/", include("moderation.urls")),
    path("interacoes/", include("interactions.urls")),
    path("admin/", admin.site.urls),
]
