from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from profiles.models import Profile

from .models import AuditLog


ACTION_CONFIG = {
    "approve": {
        "status": Profile.Status.APPROVED,
        "audit_action": "profile.approved",
        "requires_reason": False,
        "allowed": {Profile.Status.PENDING, Profile.Status.CHANGES_PENDING},
    },
    "reject": {
        "status": Profile.Status.REJECTED,
        "audit_action": "profile.rejected",
        "requires_reason": True,
        "allowed": {Profile.Status.PENDING, Profile.Status.CHANGES_PENDING},
    },
    "request_changes": {
        "status": Profile.Status.DRAFT,
        "audit_action": "profile.changes_requested",
        "requires_reason": True,
        "allowed": {Profile.Status.PENDING, Profile.Status.CHANGES_PENDING},
    },
    "suspend": {
        "status": Profile.Status.SUSPENDED,
        "audit_action": "profile.suspended",
        "requires_reason": True,
        "allowed": {
            Profile.Status.PENDING,
            Profile.Status.APPROVED,
            Profile.Status.REJECTED,
            Profile.Status.CHANGES_PENDING,
        },
    },
    "restore": {
        "status": Profile.Status.DRAFT,
        "audit_action": "profile.restored",
        "requires_reason": True,
        "allowed": {Profile.Status.SUSPENDED},
    },
}


@transaction.atomic
def moderate_profile(profile, actor, action, reason=""):
    try:
        config = ACTION_CONFIG[action]
    except KeyError as error:
        raise ValidationError("Ação de moderação inválida.") from error

    locked_profile = Profile.objects.select_for_update().select_related("user").get(pk=profile.pk)
    clean_reason = reason.strip()
    if locked_profile.status not in config["allowed"]:
        raise ValidationError("Esta ação não é válida para o estado atual do perfil.")
    if config["requires_reason"] and not clean_reason:
        raise ValidationError("Indica o motivo da decisão.")

    previous_status = locked_profile.status
    now = timezone.now()
    locked_profile.status = config["status"]
    locked_profile.is_public = action == "approve"
    locked_profile.review_note = clean_reason
    locked_profile.reviewed_by = actor
    locked_profile.reviewed_at = now
    if action == "approve":
        locked_profile.approved_at = now
    elif action in {"reject", "request_changes", "suspend", "restore"}:
        locked_profile.approved_at = None
    locked_profile.save(
        update_fields=(
            "status",
            "is_public",
            "review_note",
            "reviewed_by",
            "reviewed_at",
            "approved_at",
            "updated_at",
        )
    )

    if action == "suspend":
        locked_profile.user.is_active = False
        locked_profile.user.save(update_fields=("is_active",))
    elif action == "restore":
        locked_profile.user.is_active = True
        locked_profile.user.save(update_fields=("is_active",))

    AuditLog.objects.create(
        actor=actor,
        action=config["audit_action"],
        target_type="profile",
        target_id=str(locked_profile.pk),
        metadata={"previous_status": previous_status, "new_status": locked_profile.status},
    )
    return locked_profile

