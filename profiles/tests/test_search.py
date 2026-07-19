from django.contrib.auth import get_user_model
from django.test import TestCase

from profiles.models import Profile
from taxonomy.models import Area, Sector, Skill, Specialization


class PublicSearchTests(TestCase):
    def setUp(self):
        self.sector = Sector.objects.create(name="Tecnologia", slug="tecnologia")
        self.area = Area.objects.create(
            sector=self.sector,
            name="Desenvolvimento de software",
            slug="desenvolvimento-software",
        )
        self.specialization = Specialization.objects.create(
            area=self.area,
            name="Desenvolvimento Web",
            slug="desenvolvimento-web",
        )
        self.skill = Skill.objects.create(name="Django", slug="django")
        self.skill.specializations.add(self.specialization)
        self.public_profile = self.create_profile(
            "maria@example.com",
            "Maria Sambu",
            "Programadora Django",
            approved=True,
        )
        self.private_profile = self.create_profile(
            "privado@example.com",
            "Perfil Privado",
            "Programador Django",
            approved=False,
        )

    def create_profile(self, email, name, title, approved):
        user = get_user_model().objects.create_user(email=email, password="Segura2026!")
        profile = user.profile
        profile.public_name = name
        profile.professional_title = title
        profile.bio = "Experiência em projetos digitais e desenvolvimento web."
        profile.location = "Bissau"
        profile.phone = "+245 000 0000"
        profile.status = Profile.Status.APPROVED if approved else Profile.Status.DRAFT
        profile.is_public = approved
        profile.save()
        profile.specializations.add(self.specialization)
        profile.skills.add(self.skill)
        return profile

    def test_search_returns_only_approved_public_profiles(self):
        response = self.client.get("/pesquisar/", {"q": "Django"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Maria Sambu")
        self.assertNotContains(response, "Perfil Privado")

    def test_search_filters_by_skill_and_location(self):
        response = self.client.get(
            "/pesquisar/",
            {"skill": self.skill.slug, "location": "Bissau"},
        )

        self.assertContains(response, "Maria Sambu")

    def test_public_profile_hides_private_contacts(self):
        response = self.client.get(f"/profissionais/{self.public_profile.slug}/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Maria Sambu")
        self.assertNotContains(response, self.public_profile.user.email)
        self.assertNotContains(response, self.public_profile.phone)

    def test_private_profile_returns_not_found(self):
        response = self.client.get(f"/profissionais/{self.private_profile.slug}/")

        self.assertEqual(response.status_code, 404)

    def test_area_page_lists_only_public_professionals(self):
        response = self.client.get(f"/areas/{self.area.slug}/")

        self.assertContains(response, "Maria Sambu")
        self.assertNotContains(response, "Perfil Privado")
