from random import random
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail import get_connection
from django_email_multibackend import conf
from django.utils.importlib import import_module


def weighted_choice_by_val(choices, random_value):
    values, weights = zip(*choices)
    rnd = random_value * sum(weights)
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:
            return values[i]
    return values[-1]

def weighted_choice(choices):
    random_value = random()
    return weighted_choice_by_val(choices, random_value)

def get_backend_routing_conditions(backend):
    """
    Loads and initialise the list of conditions for :backend


    eg. 

    EMAIL_BACKENDS_CONDITIONS = {
        'mailjet': [
            ('django_email_multibackend.conditions.ExcludeMailByHeader', {'header': ('X-MAIL-TYPE', 'non-transactional')})
        ]
    }

    >>> conditions = get_backend_routing_conditions('mailchimp')
    >>> conditions[0].params
    {}

    >>> conditions = get_backend_routing_conditions('mailjet')
    >>> conditions[0].params
    {'header': ('X-MAIL-TYPE', 'non-transactional')}

    """
    paths_kwargs = conf.EMAIL_BACKENDS_CONDITIONS.get(
        backend, conf.DEFAULT_CONDITIONS
    )
    conditions = []
    for kls_conf in paths_kwargs:
        try:
            kls_name, params = kls_conf
        except ValueError:
            kls_name, params = kls_conf[0], {}
        conditions.append(load_class(kls_name)(**params))
    return conditions

def load_class(path):
    """
    Loads a class from its path

    >>> load_class('django_email_multibackend.conditions.MatchAll')
    <class 'django_email_multibackend.conditions.MatchAll'>
    """
    try:
        mod_name, klass_name = path.rsplit('.', 1)
        mod = import_module(mod_name)
    except ImportError as e:
        raise ImproperlyConfigured(('Error importing email backend module %s: "%s"'
                                    % (mod_name, e)))
    try:
        klass = getattr(mod, klass_name)
    except AttributeError:
        raise ImproperlyConfigured(('Module "%s" does not define a '
                                    '"%s" class' % (mod_name, klass_name)))
    return klass

class EmailMultiServerBackend(BaseEmailBackend):

    def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, fail_silently=False, backends=conf.EMAIL_BACKENDS,
                 backend_weights=conf.EMAIL_BACKENDS_WEIGHTS, **kwargs):

        self.servers = {}
        self.weights = self.backends_weights(
            backend_weights, backends
        )

        not_supported_params = (host, port, username, password, use_tls)

        if kwargs or any(not_supported_params):
            raise TypeError('You cant initialise this backend with %r' % not_supported_params)

        for backend_key, backend_settings in backends.items():
            backend_settings['fail_silently'] = fail_silently
            self.servers[backend_key] = get_connection(**backend_settings)

        self.validate_settings()

    def backends_weights(self, weights, backends):
        return weights or [(k,1) for k in backends.keys()]

    def validate_settings(self):
        backends, weights = zip(*self.weights)
        for backend in self.servers.keys():
            if not backend in backends:
                raise ImproperlyConfigured('Some of the backends in EMAIL_BACKENDS have not weights defined')

    def get_backends_for_email(self, mail):
        backends_weights = []
        for backend, weight in self.weights:
            conditions = get_backend_routing_conditions(backend)
            if all(cond(mail) for cond in conditions):
                backends_weights.append((backend, weight))
        return backends_weights

    def get_backend(self, email):
        backends_weights = self.get_backends_for_email(email)
        backend_key = weighted_choice(backends_weights)
        return self.servers[backend_key]

    def send_messages(self, email_messages):
        send_count = 0

        if not hasattr(email_messages, '__iter__'):
            email_messages = [email_messages]

        for email in email_messages:
            backend = self.get_backend(email)
            count = backend.send_messages([email, ])
            if count:
                send_count += count
        return send_count
