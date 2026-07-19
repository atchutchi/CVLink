from django.contrib.auth import get_user_model
from django.test import TestCase


class PublicProfileIdentityTests(TestCase):
    def test_profile_receives_unique_slug(self):
        first = get_user_model().objects.create_user(
            email="maria1@example.com",
            password="PalavraPasseSegura2026!",
            first_name="Maria",
            last_name="Sambu",
        )
        second = get_user_model().objects.create_user(
            email="maria2@example.com",
            password="PalavraPasseSegura2026!",
            first_name="Maria",
            last_name="Sambu",
        )

        self.assertTrue(first.profile.slug.startswith("maria-sambu"))
        self.assertTrue(second.profile.slug.startswith("maria-sambu"))
        self.assertNotEqual(first.profile.slug, second.profile.slug)

    def test_slug_does_not_change_with_public_name(self):
        user = get_user_model().objects.create_user(
            email="joao@example.com",
            password="PalavraPasseSegura2026!",
            first_name="João",
            last_name="Mendes",
        )
        original_slug = user.profile.slug

        user.profile.public_name = "João da Silva Mendes"
        user.profile.save()

        self.assertEqual(user.profile.slug, original_slug)
