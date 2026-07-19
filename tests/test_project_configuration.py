import os
from unittest.mock import patch

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from config.settings import get_secret_key


class ProjectConfigurationTests(SimpleTestCase):
    def test_project_uses_expected_directories_and_user_model(self):
        self.assertEqual(settings.AUTH_USER_MODEL, "accounts.User")
        self.assertIn(settings.BASE_DIR / "templates", settings.TEMPLATES[0]["DIRS"])
        self.assertIn(settings.BASE_DIR / "static", settings.STATICFILES_DIRS)

    @patch.dict(os.environ, {}, clear=True)
    def test_development_can_use_local_secret_key(self):
        self.assertEqual(get_secret_key(debug=True), "development-only-secret-key")

    @patch.dict(os.environ, {}, clear=True)
    def test_production_requires_explicit_secret_key(self):
        with self.assertRaisesMessage(
            ImproperlyConfigured,
            "SECRET_KEY é obrigatória quando DEBUG=False.",
        ):
            get_secret_key(debug=False)

    @patch.dict(os.environ, {"SECRET_KEY": "uma-chave-segura-de-producao"}, clear=True)
    def test_production_uses_configured_secret_key(self):
        self.assertEqual(get_secret_key(debug=False), "uma-chave-segura-de-producao")
