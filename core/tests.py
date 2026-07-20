from django.test import TestCase
from django.contrib.auth import get_user_model

from profiles.models import Profile
from taxonomy.models import Area, Sector

from .features import FEATURES, active_features, locked_features


class HomeViewTests(TestCase):
    def test_home_page_is_available(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)


class SeoAndOperationsTests(TestCase):
    def setUp(self):
        sector = Sector.objects.create(name="Tecnologia", slug="tecnologia")
        self.area = Area.objects.create(sector=sector, name="Software", slug="software")
        owner = get_user_model().objects.create_user(email="seo@example.com", password="test-pass")
        self.profile = owner.profile
        self.profile.public_name = "Pessoa Pública"
        self.profile.professional_title = "Programadora"
        self.profile.status = Profile.Status.APPROVED
        self.profile.is_public = True
        self.profile.save()

    def test_sitemap_contains_public_profile_and_active_area(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"/profissionais/{self.profile.slug}/")
        self.assertContains(response, f"/areas/{self.area.slug}/")

    def test_robots_blocks_private_sections_and_links_sitemap(self):
        response = self.client.get("/robots.txt")
        self.assertContains(response, "Disallow: /conta/")
        self.assertContains(response, "/sitemap.xml")

    def test_public_profile_has_canonical_open_graph_and_structured_data(self):
        response = self.client.get(f"/profissionais/{self.profile.slug}/")
        self.assertContains(response, 'rel="canonical"')
        self.assertContains(response, 'property="og:title"')
        self.assertContains(response, '"@type": "Person"')

    def test_search_and_dashboard_are_not_indexed(self):
        self.assertContains(self.client.get("/pesquisar/"), 'content="noindex,nofollow"')
        self.client.force_login(self.profile.user)
        self.assertContains(self.client.get("/conta/painel/"), 'content="noindex,nofollow"')

    def test_health_endpoint_reports_success(self):
        response = self.client.get("/saude/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_home_page_presents_product_and_search(self):
        response = self.client.get("/")

        self.assertContains(response, "Quadros cabo-verdianos")
        self.assertContains(response, "PALOP")
        self.assertContains(response, "África lusófona")
        self.assertContains(response, 'name="q"')
        self.assertContains(response, "/conta/criar/")
        self.assertContains(response, "/conta/entrar/")
        self.assertContains(response, "cvlink-logo.png")
        self.assertNotContains(response, "Europa")
        self.assertNotContains(response, "europeu")

    def test_future_features_are_structured_but_locked(self):
        self.assertEqual([feature.key for feature in active_features()], ["talent_repository"])
        self.assertIn("jobs", FEATURES)
        self.assertIn("teams", FEATURES)
        self.assertIn("billing", FEATURES)
        self.assertTrue(all(not feature.public_enabled for feature in locked_features()))

        response = self.client.get("/")
        self.assertContains(response, "Vagas")
        self.assertContains(response, "Equipas de recrutamento")
        self.assertContains(response, "Planos e cobranças")
        self.assertContains(response, "Bloqueado")

    def test_home_page_declares_brand_favicon(self):
        response = self.client.get("/")

        self.assertContains(response, 'rel="icon"')
