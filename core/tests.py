from django.test import TestCase


class HomeViewTests(TestCase):
    def test_home_page_is_available(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)

    def test_home_page_presents_product_and_search(self):
        response = self.client.get("/")

        self.assertContains(response, "Liga talento a oportunidades.")
        self.assertContains(response, 'name="q"')
        self.assertContains(response, "/conta/criar/")
        self.assertContains(response, "/conta/entrar/")
        self.assertContains(response, "cvlink-logo.png")

    def test_home_page_declares_brand_favicon(self):
        response = self.client.get("/")

        self.assertContains(response, 'rel="icon"')
