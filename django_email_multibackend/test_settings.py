EMAIL_BACKENDS = {
    'mailjet': {
        'backend': 'django_email_multibackend.tests.FakeTransactionalMailBackend',
        'host': '',
        'port': '',
        'username': '',
        'password': '',
        'use_tls': '',
    },
    'mailchimp': {
        'backend': 'django_email_multibackend.tests.FakeCampaignMailBackend',
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

EMAIL_BACKENDS_CONDITIONS = {
    'mailjet': [
        ('django_email_multibackend.conditions.ExcludeMailByHeader', {'header': ('X-MAIL-TYPE', 'non-transactional')})
    ]
}

SECRET_KEY = 'just_because_django_needs_this'
