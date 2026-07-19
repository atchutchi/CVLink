from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .forms import EmailAuthenticationForm
from .views import dashboard, signup


app_name = "accounts"

urlpatterns = [
    path("criar/", signup, name="signup"),
    path(
        "entrar/",
        LoginView.as_view(
            template_name="registration/login.html",
            authentication_form=EmailAuthenticationForm,
        ),
        name="login",
    ),
    path("sair/", LogoutView.as_view(), name="logout"),
    path("painel/", dashboard, name="dashboard"),
]
