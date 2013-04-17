EMAIL_BACKENDS = {
    'mailjet': {
        'backend': 'django_email_multibackend.tests.FakeSmtpMailBackend',
        'host': '',
        'port': '',
        'username': '',
        'password': '',
        'use_tls': '',
    },
    'mailchimp': {
        'backend': 'django_email_multibackend.tests.FakeConsoleMailBackend',
        'host': '',
        'port': '',
        'username': '',
        'password': '',
        'use_tls': '',
    },
}

EMAIL_BACKENDS_WEIGHTS = (
    ('mailjet', 5), ('mailchimp', 3)
)