from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from profiles.forms import ProfileForm


class ProfileFormTests(TestCase):
    def test_accepts_pdf_up_to_five_megabytes(self):
        upload = SimpleUploadedFile("curriculo.pdf", b"%PDF-1.4\nconteudo", "application/pdf")
        form = ProfileForm(data={}, files={"cv_file": upload})

        self.assertNotIn("cv_file", form.errors)

    def test_rejects_non_pdf_file(self):
        upload = SimpleUploadedFile("curriculo.txt", b"conteudo", "text/plain")
        form = ProfileForm(data={}, files={"cv_file": upload})

        self.assertIn("cv_file", form.errors)

    def test_rejects_pdf_above_five_megabytes(self):
        upload = SimpleUploadedFile(
            "curriculo.pdf",
            b"%PDF" + (b"x" * (5 * 1024 * 1024)),
            "application/pdf",
        )
        form = ProfileForm(data={}, files={"cv_file": upload})

        self.assertIn("cv_file", form.errors)
