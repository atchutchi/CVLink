from django.http import HttpResponse, JsonResponse
from django.db import connection
from django.db.utils import OperationalError
from django.shortcuts import render
from django.urls import reverse


def home(request):
    return render(
        request,
        "core/home.html",
        {"canonical_url": request.build_absolute_uri(reverse("home"))},
    )


def robots(request):
    sitemap_url = request.build_absolute_uri(reverse("sitemap"))
    content = "\n".join(
        (
            "User-agent: *",
            "Allow: /",
            "Disallow: /conta/",
            "Disallow: /perfil/",
            "Disallow: /interacoes/",
            "Disallow: /administracao/",
            "Disallow: /admin/",
            "Disallow: /pesquisar/",
            f"Sitemap: {sitemap_url}",
        )
    )
    return HttpResponse(content, content_type="text/plain; charset=utf-8")


def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except OperationalError:
        return JsonResponse({"status": "unavailable"}, status=503)
    return JsonResponse({"status": "ok"})
