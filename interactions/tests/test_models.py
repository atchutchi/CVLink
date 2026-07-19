from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from interactions.models import Favorite, Notification, ProfileLike, Report
from profiles.models import Profile


class InteractionModelTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(email="user@example.com", password="test-pass")
        owner = user_model.objects.create_user(email="owner@example.com", password="test-pass")
        self.profile = owner.profile
        self.profile.status = Profile.Status.APPROVED
        self.profile.is_public = True
        self.profile.save()

    def test_favorite_and_like_are_unique_per_user_and_profile(self):
        Favorite.objects.create(user=self.user, profile=self.profile)
        ProfileLike.objects.create(user=self.user, profile=self.profile)

        with self.assertRaises(IntegrityError), transaction.atomic():
            Favorite.objects.create(user=self.user, profile=self.profile)
        with self.assertRaises(IntegrityError), transaction.atomic():
            ProfileLike.objects.create(user=self.user, profile=self.profile)

    def test_only_one_active_report_is_allowed(self):
        Report.objects.create(reporter=self.user, profile=self.profile, reason=Report.Reason.FRAUD)

        with self.assertRaises(IntegrityError), transaction.atomic():
            Report.objects.create(reporter=self.user, profile=self.profile, reason=Report.Reason.FALSE_DATA)

    def test_notification_starts_unread(self):
        notification = Notification.objects.create(user=self.user, type="test", title="Teste")
        self.assertIsNone(notification.read_at)

