try:
    import unittest2 as unittest
except ImportError:
    import unittest

from django_email_multibackend.backends import EmailMultiServerBackend
from django.core.mail import EmailMessage
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
from django_email_multibackend.conditions import MatchAll


class SendMailException(Exception):
    pass

class SentTransactionEmailException(SendMailException):
    pass

class SentCampaignException(SendMailException):
    pass

class FakeTransactionalMailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        raise SentTransactionEmailException()

class FakeCampaignMailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        raise SentCampaignException()


transactional_email = EmailMessage(
    'password reset', '', to=['tbarbugli@gmail.com']
)
transactional_email.extra_headers['X-MAIL-TYPE'] = 'transactional'

campaign_email = EmailMessage(
    'buy this', '', to=['tbarbugli@gmail.com']
)
campaign_email.extra_headers['X-MAIL-TYPE'] = 'non-transactional'

class TestMultiBackendEmail(unittest.TestCase):

    def test_init(self):
        EmailMultiServerBackend()

    def test_default_weights(self):
        instance = EmailMultiServerBackend()
        backends = dict.fromkeys(['b1', 'b2'])
        weights = instance.backends_weights(None, backends)
        self.assertListEqual(list(zip(*weights)[0]), backends.keys())

    def test_weights(self):
        instance = EmailMultiServerBackend()
        assert(instance.weights == settings.EMAIL_BACKENDS_WEIGHTS)

    def test_get_backend(self):
        instance = EmailMultiServerBackend()
        for i in range(10):
            assert instance.get_backend(campaign_email) in instance.servers.values()

    def test_send_message(self):
        instance = EmailMultiServerBackend()
        self.assertRaises(SendMailException, instance.send_messages, transactional_email)

    def test_send_messages(self):
        mails = [transactional_email, campaign_email]
        instance = EmailMultiServerBackend()
        self.assertRaises(SendMailException, instance.send_messages, mails)

    def test_backend_classes(self):
        instance = EmailMultiServerBackend()
        for backend_name, backend in instance.servers.items():
            assert isinstance(backend, (FakeTransactionalMailBackend, FakeCampaignMailBackend))

class TestConditions(unittest.TestCase):

    def test_send_non_email(self):
        self.assertRaises(TypeError, MatchAll(), None)

    def test_match_all_backends(self):
        instance = EmailMultiServerBackend()
        transactional_backends = instance.get_backends_for_email(transactional_email)
        assert transactional_backends == list(instance.weights)

    def test_filtered_backends(self):
        instance = EmailMultiServerBackend()
        transactional_backends = instance.get_backends_for_email(campaign_email)
        assert transactional_backends == [('mailchimp', 3)]
