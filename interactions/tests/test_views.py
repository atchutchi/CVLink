from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from interactions.models import ContactRequest, Favorite, Notification, ProfileLike, Report
from profiles.models import Profile


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class InteractionViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(email="user@example.com", password="test-pass")
        self.owner = user_model.objects.create_user(email="owner@example.com", password="test-pass")
        self.profile = self.owner.profile
        self.profile.public_name = "Profissional Público"
        self.profile.status = Profile.Status.APPROVED
        self.profile.is_public = True
        self.profile.consent_contact = True
        self.profile.save()

    def test_favorite_toggle_adds_and_removes_profile(self):
        self.client.force_login(self.user)
        url = reverse("interactions:favorite-toggle", args=(self.profile.slug,))

        self.client.post(url)
        self.assertTrue(Favorite.objects.filter(user=self.user, profile=self.profile).exists())
        self.client.post(url)
        self.assertFalse(Favorite.objects.filter(user=self.user, profile=self.profile).exists())

    def test_like_toggle_updates_total(self):
        self.client.force_login(self.user)
        self.client.post(reverse("interactions:like-toggle", args=(self.profile.slug,)))
        self.assertEqual(ProfileLike.objects.filter(profile=self.profile).count(), 1)

    def test_owner_cannot_interact_with_own_profile(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("interactions:favorite-toggle", args=(self.profile.slug,)))
        self.assertEqual(response.status_code, 403)

    def test_contact_creates_private_request_notification_and_email(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("interactions:contact", args=(self.profile.slug,)),
            {"subject": "Proposta de projecto", "message": "Gostaria de apresentar uma oportunidade profissional."},
        )

        self.assertRedirects(response, reverse("interactions:contacts"))
        self.assertTrue(ContactRequest.objects.filter(sender=self.user, profile=self.profile).exists())
        self.assertTrue(Notification.objects.filter(user=self.owner, type="new_contact").exists())
        self.assertEqual(len(mail.outbox), 1)

    def test_contact_rate_limit_blocks_fourth_message_in_one_hour(self):
        self.client.force_login(self.user)
        url = reverse("interactions:contact", args=(self.profile.slug,))
        payload = {"subject": "Proposta", "message": "Mensagem profissional suficientemente clara."}
        for _index in range(3):
            self.client.post(url, payload)

        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "limite de mensagens")
        self.assertEqual(ContactRequest.objects.count(), 3)

    def test_hidden_contact_preference_blocks_message(self):
        self.profile.contact_visibility = Profile.ContactVisibility.HIDDEN
        self.profile.save()
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("interactions:contact", args=(self.profile.slug,)),
            {"subject": "Proposta", "message": "Mensagem profissional suficientemente clara."},
        )
        self.assertContains(response, "não está a aceitar contactos")
        self.assertFalse(ContactRequest.objects.exists())

    def test_recipient_can_report_abusive_contact(self):
        contact = ContactRequest.objects.create(
            sender=self.user,
            profile=self.profile,
            subject="Mensagem",
            message="Conteúdo recebido.",
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("interactions:contact-action", args=(contact.pk,)),
            {"action": "report"},
        )
        self.assertRedirects(response, reverse("interactions:contacts"))
        contact.refresh_from_db()
        self.assertEqual(contact.status, ContactRequest.Status.REPORTED)

    def test_duplicate_open_report_is_rejected(self):
        self.client.force_login(self.user)
        url = reverse("interactions:report", args=(self.profile.slug,))
        self.client.post(url, {"reason": "fraud", "description": "Informação suspeita."})

        response = self.client.post(url, {"reason": "false_data", "description": "Repetida."})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "denúncia activa")
        self.assertEqual(Report.objects.count(), 1)

    def test_notification_can_be_marked_as_read_only_by_owner(self):
        notification = Notification.objects.create(user=self.user, type="test", title="Teste")
        self.client.force_login(self.user)
        response = self.client.post(reverse("interactions:notification-read", args=(notification.pk,)))

        self.assertRedirects(response, reverse("interactions:notifications"))
        notification.refresh_from_db()
        self.assertIsNotNone(notification.read_at)
