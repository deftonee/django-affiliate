# -*- coding: utf-8 -*-
from datetime import timedelta
from importlib import reload

from django.test import TestCase
from django.utils import timezone

from django.urls import reverse

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.test.utils import override_settings
from model_bakery import baker
from freezegun import freeze_time

from affiliate import app_settings
from .utils import get_aid_url, modify_settings


class TestAffiliateMiddleware(TestCase):
    def test_no_affiliate_in_url(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.context[0].request.affiliate.exists())

    def test_bad_affiliate_code(self):
        resp = self.client.get(get_aid_url('/', 123))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.context[0].request.affiliate.exists())

    def test_bad_affiliate_code_type(self):
        resp = self.client.get(get_aid_url('/', 'nailgun'))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.context[0].request.affiliate.exists())

    def test_affiliate_assigned(self):
        affiliate = baker.make(settings.AFFILIATE_AFFILIATE_MODEL)
        resp = self.client.get(get_aid_url('/', affiliate.aid))
        self.assertEqual(resp.status_code, 200)
        affiliate_resp = resp.context[0].request.affiliate
        self.assertTrue(affiliate_resp.exists())
        self.assertEqual(affiliate.aid, affiliate_resp.aid)

    def test_previous_affiliate_is_used(self):
        affiliate = baker.make(settings.AFFILIATE_AFFILIATE_MODEL)
        resp = self.client.get(get_aid_url('/', affiliate.aid))
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get(get_aid_url('/', affiliate.aid + 100))  # invalid aid code
        self.assertEqual(resp.status_code, 200)
        affiliate_resp = resp.context[0].request.affiliate
        self.assertTrue(affiliate_resp.exists())
        self.assertEqual(affiliate.aid, affiliate_resp.aid)

    def test_affiliate_saved_in_session(self):
        affiliate = baker.make(settings.AFFILIATE_AFFILIATE_MODEL)
        self.client.get(get_aid_url('/', affiliate.aid))

        # next response without aid still contains affiliate
        with freeze_time(timezone.now() + timedelta(seconds=app_settings.SESSION_AGE - 1)):
            resp = self.client.get('/')

        self.assertEqual(resp.status_code, 200)
        affiliate_resp = resp.context[0].request.affiliate
        self.assertTrue(affiliate_resp.exists())
        self.assertEqual(affiliate.aid, affiliate_resp.aid)

    def test_affiliate_session_expired(self):
        affiliate = baker.make(settings.AFFILIATE_AFFILIATE_MODEL)
        self.client.get(get_aid_url('/', affiliate.aid))

        # affiliate is expired
        with freeze_time(timezone.now() + timedelta(seconds=app_settings.SESSION_AGE + 1)):
            resp = self.client.get('/')

        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.context[0].request.affiliate.exists())

    def test_previous_affiliate_session_expired(self):
        affiliate = baker.make(settings.AFFILIATE_AFFILIATE_MODEL)
        resp = self.client.get(get_aid_url('/', affiliate.aid))
        self.assertEqual(resp.status_code, 200)

        # affiliate is expired
        with freeze_time(timezone.now() + timedelta(seconds=app_settings.SESSION_AGE + 1)):
            resp = self.client.get(get_aid_url('/', affiliate.aid + 100))  # invalid aid code

        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.context[0].request.affiliate.exists())

    def test_affiliate_code_in_post_request(self):
        affiliate = baker.make(settings.AFFILIATE_AFFILIATE_MODEL)
        resp = self.client.post(get_aid_url(reverse('users:signup'), affiliate.aid),
                                dict(username='newuser', password1='123456', password2='123456'))
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get('/')
        self.assertTrue(resp.context[0].request.affiliate.exists())
        self.assertEqual(resp.context[0].request.affiliate.pk, affiliate.pk)


@override_settings(AFFILIATE_REMOVE_PARAM_AND_REDIRECT=True)
class TestAffiliateMiddlewareRemoveAndRedirect(TestCase):
    def setUp(self):
        super(TestAffiliateMiddlewareRemoveAndRedirect, self).setUp()
        reload(app_settings)

    def test_affiliate_code_remove_from_url(self):
        affiliate = baker.make(settings.AFFILIATE_AFFILIATE_MODEL)
        resp = self.client.get(get_aid_url('/', affiliate.aid))
        self.assertRedirects(resp, '/')
        resp = self.client.get('/')
        self.assertTrue(resp.context[0].request.affiliate.exists())
        self.assertEqual(resp.context[0].request.affiliate.pk, affiliate.pk)

    def test_affiliate_code_remove_from_url_other_params_kept(self):
        affiliate = baker.make(settings.AFFILIATE_AFFILIATE_MODEL)
        resp = self.client.get(get_aid_url('/', affiliate.aid) + '&other=param')
        self.assertRedirects(resp, '/?other=param')
        resp = self.client.get('/')
        self.assertTrue(resp.context[0].request.affiliate.exists())
        self.assertEqual(resp.context[0].request.affiliate.pk, affiliate.pk)


@modify_settings(MIDDLEWARE={
    'remove': [
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ],
}, INSTALLED_APPS={
    'remove': [
        'django.contrib.sessions'
    ]
})
class TestAffiliateMiddlewareNoSession(TestCase):
    def setUp(self):
        super(TestAffiliateMiddlewareNoSession, self).setUp()
        reload(app_settings)

    def test_no_session_affiliate_in_url(self):
        app_settings.SAVE_IN_SESSION = False

        affiliate = baker.make(settings.AFFILIATE_AFFILIATE_MODEL)
        resp = self.client.get(get_aid_url('/', affiliate.aid))
        self.assertEqual(resp.status_code, 200)
        affiliate_resp = resp.context[0].request.affiliate
        self.assertTrue(affiliate_resp.exists())
        self.assertEqual(affiliate.aid, affiliate_resp.aid)

        # next request can't remember previous affiliate
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.context[0].request.affiliate.exists())

    def test_no_session_exception_raised(self):
        app_settings.SAVE_IN_SESSION = True

        affiliate = baker.make(settings.AFFILIATE_AFFILIATE_MODEL)
        with self.assertRaises(ImproperlyConfigured):
            self.client.get(get_aid_url('/', affiliate.aid))
