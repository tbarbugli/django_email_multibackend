Django Email Multibackend
=========================

A simple weighted email multi backend for django.

This packages allows you to use multiple email backends and distribute the emails with configurable weights.

Settings:

**EMAIL\_BACKENDS**  
A dictonary that defines the available backends

**EMAIL\_BACKENDS\_WEIGHTS**  
A tuple of (backend_name, weight) that defines the weights used to distribute
the emails among backends.
This setting is optional, when not defined emails are going to be distributed evenly
across the backends

Example settings:

    EMAIL_BACKENDS = {
        'mailjet': {
            'backend': 'django.core.mail.backends.smtp.EmailBackend',
            'host': 'in.mailjet.com',
            'port': '25',
            'username': 'username',
            'password': 'secret',
            'use_tls': False
        },
        'mandarill': {
            'backend': 'django.core.mail.backends.smtp.EmailBackend',
            'host': 'in.mandarill.com',
            'port': '587',
            'username': 'user',
            'password': 'pass',
            'use_tls': True
        },
    }

    EMAIL_BACKENDS\_WEIGHTS = (
        ('mailjet', 7), ('mandarill', 3)
    )

    EMAIL_BACKEND = 'django_email_multibackend.backends.EmailMultiServerBackend'


With this setting 70% of emails will be sent via mailjet and 30% via mandarill.
