from django.conf import settings
from django.db import models

from taxonomy.models import Skill, Specialization


class Profile(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Rascunho"
        PENDING = "pending", "Pendente"
        APPROVED = "approved", "Aprovado"
        REJECTED = "rejected", "Rejeitado"
        CHANGES_PENDING = "changes_pending", "Alterações pendentes"
        SUSPENDED = "suspended", "Suspenso"
        ARCHIVED = "archived", "Arquivado"
        DELETED = "deleted", "Eliminado"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="utilizador",
        related_name="profile",
        on_delete=models.CASCADE,
    )
    public_name = models.CharField("nome público", max_length=160, blank=True)
    professional_title = models.CharField("título profissional", max_length=180, blank=True)
    bio = models.TextField("biografia", blank=True)
    location = models.CharField("localização", max_length=160, blank=True)
    photo = models.ImageField("fotografia", upload_to="profile_photos/%Y/%m/", blank=True)
    status = models.CharField(
        "estado",
        max_length=24,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    is_public = models.BooleanField("público", default=False, db_index=True)
    specializations = models.ManyToManyField(
        Specialization,
        verbose_name="especializações",
        related_name="profiles",
        blank=True,
    )
    skills = models.ManyToManyField(
        Skill,
        verbose_name="competências",
        related_name="profiles",
        blank=True,
    )
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "perfil profissional"
        verbose_name_plural = "perfis profissionais"
        ordering = ("public_name", "user__email")

    def __str__(self):
        return self.public_name or self.user.email
