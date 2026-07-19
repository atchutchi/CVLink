from django.urls import path

from .views import (
    contact,
    contact_action,
    contacts,
    favorite_toggle,
    favorites,
    like_toggle,
    notification_read,
    notifications,
    report,
)


app_name = "interactions"

urlpatterns = [
    path("favoritos/", favorites, name="favorites"),
    path("favoritos/<slug:slug>/alternar/", favorite_toggle, name="favorite-toggle"),
    path("gostos/<slug:slug>/alternar/", like_toggle, name="like-toggle"),
    path("contactar/<slug:slug>/", contact, name="contact"),
    path("contactos/", contacts, name="contacts"),
    path("contactos/<int:pk>/acao/", contact_action, name="contact-action"),
    path("denunciar/<slug:slug>/", report, name="report"),
    path("notificacoes/", notifications, name="notifications"),
    path("notificacoes/<int:pk>/ler/", notification_read, name="notification-read"),
]
