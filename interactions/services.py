from datetime import timedelta
from hashlib import sha256

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from profiles.models import Profile

from .models import ContactRequest, Favorite, Notification, ProfileLike, Report


def ensure_external_profile_action(user, profile):
    if profile.user_id == user.id:
        raise PermissionDenied("Não podes executar esta ação no teu próprio perfil.")
    if profile.status != Profile.Status.APPROVED or not profile.is_public:
        raise PermissionDenied("Este perfil não está disponível.")


def toggle_relation(model, user, profile):
    ensure_external_profile_action(user, profile)
    relation, created = model.objects.get_or_create(user=user, profile=profile)
    if not created:
        relation.delete()
    return created


def toggle_favorite(user, profile):
    return toggle_relation(Favorite, user, profile)


def toggle_like(user, profile):
    return toggle_relation(ProfileLike, user, profile)


@transaction.atomic
def create_contact(sender, profile, subject, message, remote_address=""):
    ensure_external_profile_action(sender, profile)
    if not sender.email_verified_at:
        raise ValidationError("Confirma o teu email antes de enviares contactos.")
    if not profile.consent_contact or profile.contact_visibility == Profile.ContactVisibility.HIDDEN:
        raise ValidationError("Este profissional não está a aceitar contactos.")
    since = timezone.now() - timedelta(hours=1)
    recent_count = ContactRequest.objects.filter(
        sender=sender, profile=profile, created_at__gte=since
    ).count()
    if recent_count >= 3:
        raise ValidationError("Atingiste o limite de mensagens para este perfil. Tenta novamente mais tarde.")
    ip_hash = sha256(f"{settings.SECRET_KEY}:{remote_address}".encode()).hexdigest() if remote_address else ""
    contact = ContactRequest.objects.create(
        sender=sender,
        profile=profile,
        subject=subject,
        message=message,
        sender_ip_hash=ip_hash,
    )
    Notification.objects.create(
        user=profile.user,
        type="new_contact",
        title="Novo pedido de contacto",
        body=f"Recebeste uma mensagem sobre: {subject}",
        link=reverse("interactions:contacts"),
    )
    send_mail(
        subject=f"CVLink: {subject}",
        message="Recebeste um novo pedido de contacto. Inicia sessão no CVLink para consultar a mensagem.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[profile.user.email],
        fail_silently=True,
    )
    return contact


@transaction.atomic
def create_report(reporter, profile, reason, description=""):
    ensure_external_profile_action(reporter, profile)
    if Report.objects.filter(
        reporter=reporter,
        profile=profile,
        status__in=(Report.Status.OPEN, Report.Status.REVIEWING),
    ).exists():
        raise ValidationError("Já existe uma denúncia activa para este perfil.")
    report = Report.objects.create(
        reporter=reporter, profile=profile, reason=reason, description=description
    )
    staff_ids = profile.user.__class__.objects.filter(is_staff=True, is_active=True).values_list("id", flat=True)
    Notification.objects.bulk_create(
        [
            Notification(
                user_id=user_id,
                type="new_report",
                title="Nova denúncia de perfil",
                body=f"Foi criada uma denúncia para {profile}.",
                link=reverse("moderation:report-list"),
            )
            for user_id in staff_ids
        ]
    )
    return report
