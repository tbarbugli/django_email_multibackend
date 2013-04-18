import threading
from random import random
from bisect import bisect
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail import get_connection

def weighted_choice(choices):
    values, weights = zip(*choices)
    total = 0
    cum_weights = []
    for w in weights:
        total += w
        cum_weights.append(total)
    x = random() * total
    i = bisect(cum_weights, x)
    return values[i]

class EmailMultiServerBackend(BaseEmailBackend):

    def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, fail_silently=False, **kwargs):

        self.servers = {}
        self.weights = self.backends_weights(
            settings.EMAIL_BACKENDS_WEIGHTS, settings.EMAIL_BACKENDS
        )

        not_supported_params = (host, port, username, password, use_tls)
        if kwargs or any(not_supported_params):
            raise TypeError('You cant initialise this backend with any of this params %r' % not_supported_params)

        for backend_key, backend_settings in settings.EMAIL_BACKENDS.iteritems():
            backend_settings['fail_silently'] = fail_silently
            self.servers[backend_key] = get_connection(**backend_settings)

        self.validate_settings()
        self._lock = threading.RLock()

    def backends_weights(self, weights, backends):
        """
        if weights are not defined defaults to even weights

        """
        return weights or [(k,1) for k in backends.keys()]

    def validate_settings(self):
        backends, weights = zip(*self.weights)
        for backend in self.servers.keys():
            if not backend in backends:
                raise TypeError('Some of the backends in EMAIL_BACKENDS have not weights defined')

    def get_backend(self):
        backend_key = weighted_choice(self.weights)
        return self.servers[backend_key]

    def send_messages(self, email_messages):
        backend = self.get_backend()
        return backend.send_messages(email_messages)
