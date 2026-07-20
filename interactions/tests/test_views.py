from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from interactions.models import ContactRequest, Favorite, Notification, ProfileLike, Report, SavedSearch
from profiles.models import Profile


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class InteractionViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(email="user@example.com", password="test-pass")
        self.user.email_verified_at = timezone.now()
        self.user.save(update_fields=("email_verified_at",))
        self.owner = user_model.objects.create_user(email="owner@example.com", password="test-pass")
        self.other_user = user_model.objects.create_user(email="other@example.com", password="test-pass")
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

    def test_unverified_sender_cannot_contact(self):
        self.user.email_verified_at = None
        self.user.save(update_fields=("email_verified_at",))
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("interactions:contact", args=(self.profile.slug,)),
            {"subject": "Proposta", "message": "Mensagem profissional suficientemente clara."},
        )
        self.assertContains(response, "Confirma o teu email")
        self.assertFalse(ContactRequest.objects.exists())

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

    def test_favorite_update_saves_status_notes_and_tags(self):
        favorite = Favorite.objects.create(user=self.user, profile=self.profile)
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("interactions:favorite-update", args=(favorite.pk,)),
            {"status": "interview", "notes": "Boa entrevista", "tags": "civil, senior"},
        )

        self.assertRedirects(response, reverse("interactions:favorites"))
        favorite.refresh_from_db()
        self.assertEqual(favorite.status, Favorite.Status.INTERVIEW)
        self.assertEqual(favorite.notes, "Boa entrevista")
        self.assertEqual(set(favorite.tags.values_list("name", flat=True)), {"civil", "senior"})

    def test_favorite_update_returns_404_for_another_users_favorite(self):
        other_favorite = Favorite.objects.create(user=self.other_user, profile=self.profile)
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("interactions:favorite-update", args=(other_favorite.pk,)), {"status": "interview"}
        )

        self.assertEqual(response.status_code, 404)

    def test_new_recruitment_routes_redirect_anonymous_users_to_login(self):
        favorite = Favorite.objects.create(user=self.user, profile=self.profile)
        saved_search = SavedSearch.objects.create(user=self.user, name="Engenharia", query_params={"q": "engenheiro"})
        urls = (
            reverse("interactions:favorites"),
            reverse("interactions:favorite-update", args=(favorite.pk,)),
            reverse("interactions:saved-search-create"),
            reverse("interactions:saved-search-run", args=(saved_search.pk,)),
            reverse("interactions:saved-search-delete", args=(saved_search.pk,)),
            reverse("interactions:compare"),
            reverse("interactions:shortlist-export"),
        )

        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, f"{reverse('accounts:login')}?next={url}")

    def test_saved_search_create_cleans_params_and_redirects_to_search(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("interactions:saved-search-create"),
            {"name": "Engenharia", "q": "engenheiro", "experience": "5", "unsafe": "x"},
        )

        self.assertRedirects(response, reverse("search") + "?q=engenheiro&experience=5")
        self.assertEqual(
            SavedSearch.objects.get(user=self.user).query_params, {"q": "engenheiro", "experience": "5"}
        )

    def test_saved_search_run_redirects_to_the_saved_query(self):
        saved = SavedSearch.objects.create(
            user=self.user, name="Engenharia", query_params={"q": "engenheiro", "experience": "5"}
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("interactions:saved-search-run", args=(saved.pk,)))

        self.assertRedirects(response, reverse("search") + "?q=engenheiro&experience=5")

    def test_saved_search_run_returns_404_for_another_users_search(self):
        saved = SavedSearch.objects.create(user=self.other_user, name="Privada", query_params={"q": "privada"})
        self.client.force_login(self.user)

        response = self.client.get(reverse("interactions:saved-search-run", args=(saved.pk,)))

        self.assertEqual(response.status_code, 404)

    def test_saved_search_delete_returns_404_for_another_users_search(self):
        saved = SavedSearch.objects.create(user=self.other_user, name="Privada", query_params={"q": "privada"})
        self.client.force_login(self.user)

        response = self.client.post(reverse("interactions:saved-search-delete", args=(saved.pk,)))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(SavedSearch.objects.filter(pk=saved.pk).exists())

    def test_compare_shows_only_public_profile_data(self):
        self.profile.phone = "+351 912 345 678"
        self.profile.save(update_fields=("phone",))
        Favorite.objects.create(user=self.user, profile=self.profile)
        self.client.force_login(self.user)

        response = self.client.get(reverse("interactions:compare"), {"profiles": str(self.profile.pk)})

        self.assertContains(response, self.profile.public_display_name)
        self.assertNotContains(response, self.profile.phone)

    def test_compare_hides_city_and_country_when_location_is_private(self):
        self.profile.location = "Quebo"
        self.profile.country = "Guiné-Bissau"
        self.profile.location_is_public = False
        self.profile.save(update_fields=("location", "country", "location_is_public"))
        Favorite.objects.create(user=self.user, profile=self.profile)
        self.client.force_login(self.user)

        response = self.client.get(reverse("interactions:compare"), {"profiles": str(self.profile.pk)})

        self.assertNotContains(response, "Quebo")
        self.assertNotContains(response, "Guiné-Bissau")

    def test_compare_ignores_profiles_outside_users_shortlist(self):
        other_owner = get_user_model().objects.create_user(email="outro-perfil@example.com", password="test-pass")
        other_profile = other_owner.profile
        other_profile.public_name = "Perfil de outra shortlist"
        other_profile.status = Profile.Status.APPROVED
        other_profile.is_public = True
        other_profile.save()
        Favorite.objects.create(user=self.other_user, profile=other_profile)
        self.client.force_login(self.user)

        response = self.client.get(reverse("interactions:compare"), {"profiles": str(other_profile.pk)})

        self.assertNotContains(response, other_profile.public_display_name)

    def test_shortlist_export_excludes_private_email(self):
        Favorite.objects.create(user=self.user, profile=self.profile)
        self.client.force_login(self.user)

        response = self.client.get(reverse("interactions:shortlist-export"))

        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertNotContains(response, self.profile.user.email)

    def test_shortlist_export_excludes_another_users_favorite(self):
        other_owner = get_user_model().objects.create_user(email="exportar-outro@example.com", password="test-pass")
        other_profile = other_owner.profile
        other_profile.public_name = "Perfil privado de outra shortlist"
        other_profile.status = Profile.Status.APPROVED
        other_profile.is_public = True
        other_profile.save()
        Favorite.objects.create(user=self.other_user, profile=other_profile, notes="Nota privada")
        self.client.force_login(self.user)

        response = self.client.get(reverse("interactions:shortlist-export"))

        self.assertNotContains(response, other_profile.public_display_name)
        self.assertNotContains(response, "Nota privada")
