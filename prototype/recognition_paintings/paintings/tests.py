from io import BytesIO
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image


class MainPageTests(TestCase):
    def test_home_page_is_available(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Surreal Meter")

    def test_rejects_non_image_upload(self):
        upload = SimpleUploadedFile("notes.txt", b"not an image", content_type="text/plain")
        response = self.client.post(reverse("index"), {"image": upload})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Не удалось прочитать изображение")

    @patch("paintings.ml.classifier.classify_image", return_value={
        "dali": 65.0, "magritte": 10.0, "ernst": 10.0, "miro": 10.0, "other": 5.0,
    })
    def test_valid_image_returns_classification(self, classify_mock):
        buffer = BytesIO()
        Image.new("RGB", (32, 32), color="white").save(buffer, format="PNG")
        upload = SimpleUploadedFile("test.png", buffer.getvalue(), content_type="image/png")
        response = self.client.post(reverse("index"), {"image": upload})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Сальвадор Дали")
        self.assertContains(response, "65.0%")
        classify_mock.assert_called_once()
