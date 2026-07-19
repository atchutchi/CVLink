from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from profiles.selectors import public_profiles

from .forms import ContactRequestForm, ReportForm
from .models import ContactRequest, Favorite, Notification
from .services import create_contact, create_report, toggle_favorite, toggle_like


def get_public_profile(slug):
    return get_object_or_404(public_profiles(), slug=slug)


@login_required
@require_POST
def favorite_toggle(request, slug):
    profile = get_public_profile(slug)
    added = toggle_favorite(request.user, profile)
    messages.success(request, "Perfil guardado." if added else "Perfil removido dos favoritos.")
    return redirect("public-profile", slug=profile.slug)


@login_required
@require_POST
def like_toggle(request, slug):
    profile = get_public_profile(slug)
    added = toggle_like(request.user, profile)
    messages.success(request, "Gosto registado." if added else "Gosto removido.")
    return redirect("public-profile", slug=profile.slug)


@login_required
def contact(request, slug):
    profile = get_public_profile(slug)
    form = ContactRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            create_contact(
                request.user,
                profile,
                form.cleaned_data["subject"],
                form.cleaned_data["message"],
                request.META.get("REMOTE_ADDR", ""),
            )
        except ValidationError as exception:
            form.add_error(None, exception.messages[0])
        else:
            messages.success(request, "Pedido de contacto enviado com sucesso.")
            return redirect("interactions:contacts")
    return render(request, "interactions/contact_form.html", {"form": form, "profile": profile})


@login_required
def report(request, slug):
    profile = get_public_profile(slug)
    form = ReportForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            create_report(
                request.user,
                profile,
                form.cleaned_data["reason"],
                form.cleaned_data["description"],
            )
        except ValidationError as exception:
            form.add_error(None, exception.messages[0])
        else:
            messages.success(request, "Denúncia enviada para análise.")
            return redirect("public-profile", slug=profile.slug)
    return render(request, "interactions/report_form.html", {"form": form, "profile": profile})


@login_required
def favorites(request):
    items = Favorite.objects.filter(
        user=request.user,
        profile__status="approved",
        profile__is_public=True,
    ).select_related("profile", "profile__user")
    return render(request, "interactions/favorites.html", {"favorites": items})


@login_required
def contacts(request):
    received = request.user.profile.contact_requests.select_related("sender")
    sent = request.user.sent_contact_requests.select_related("profile", "profile__user")
    return render(request, "interactions/contacts.html", {"received": received, "sent": sent})


@login_required
@require_POST
def contact_action(request, pk):
    contact_request = get_object_or_404(
        ContactRequest.objects.select_related("profile"), pk=pk, profile__user=request.user
    )
    action = request.POST.get("action")
    if action == "block":
        contact_request.status = ContactRequest.Status.BLOCKED
        message = "Contacto bloqueado."
    elif action == "report":
        contact_request.status = ContactRequest.Status.REPORTED
        message = "Contacto denunciado à administração."
        staff_ids = request.user.__class__.objects.filter(is_staff=True, is_active=True).values_list("id", flat=True)
        Notification.objects.bulk_create(
            [
                Notification(
                    user_id=user_id,
                    type="contact_reported",
                    title="Contacto denunciado",
                    body=f"O pedido de contacto #{contact_request.pk} foi denunciado.",
                    link="/admin/interactions/contactrequest/",
                )
                for user_id in staff_ids
            ]
        )
    else:
        messages.error(request, "Ação inválida.")
        return redirect("interactions:contacts")
    contact_request.save(update_fields=("status",))
    messages.success(request, message)
    return redirect("interactions:contacts")


@login_required
def notifications(request):
    return render(
        request,
        "interactions/notifications.html",
        {"notifications": request.user.notifications.all()[:100]},
    )


@login_required
@require_POST
def notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    if not notification.read_at:
        notification.read_at = timezone.now()
        notification.save(update_fields=("read_at",))
    return redirect("interactions:notifications")
