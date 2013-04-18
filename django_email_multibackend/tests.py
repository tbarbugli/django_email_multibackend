try:
    import unittest2 as unittest
except ImportError:
    import unittest

from django_email_multibackend.backends import EmailMultiServerBackend
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

class SendMailException(Exception):
    pass

class SmtpException(SendMailException):
    pass

class ConsoleException(SendMailException):
    pass

class FakeSmtpMailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        raise SmtpException()

class FakeConsoleMailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        raise ConsoleException()

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
            assert instance.get_backend() in instance.servers.values()

    def test_send_messages(self):
        instance = EmailMultiServerBackend()
        for i in range(10):
            with self.assertRaises((SendMailException, )):
                instance.send_messages(None)

    def test_backend_classes(self):
        instance = EmailMultiServerBackend()
        for backend_name, backend in instance.servers.items():
            assert isinstance(backend, (FakeSmtpMailBackend, FakeConsoleMailBackend))
