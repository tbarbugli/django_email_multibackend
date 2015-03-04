Django Email Multibackend
=========================

[![Build Status](https://travis-ci.org/tbarbugli/django_email_multibackend.png?cache=0)](https://travis-ci.org/tbarbugli/django_email_multibackend)

A Django email multi backend

This project aims to help with this situations:

    - e-mail provider/backends A/B testing (eg. which provider gives you better deliverability?)
    - e-mail provider migration (eg. you can use weights to ramp up traffic)
    - routing emails to backends

How it works:

When using this email backend e-mails are routed to a list of compatible backends.   
By default all backends are used, if needed it is possible to select / exclude backends (eg. exclude email with header X). 
Once the selection is done the backend chooses one of them via a random weighted choice.

Settings:
=========


**EMAIL\_BACKENDS**  
A dictonary that defines the available backends

**EMAIL\_BACKENDS\_WEIGHTS**  
A tuple of (backend_name, weight) that defines the weights used to distribute
the emails among backends.
This setting is optional, when not defined emails are going to be distributed evenly
across the backends

**EMAIL\_BACKENDS\_CONDITIONS** 
A dictonary that maps a backend to a list of conditions that needs to be 


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

    EMAIL_BACKENDS_WEIGHTS = (
        ('mailjet', 7), ('mandarill', 3)
    )

    EMAIL_BACKENDS_CONDITIONS = {
        'mandarill': ('django_email_multibackend.conditions.ExcludeMailByHeader', {'header': ('X-MAIL-TYPE', 'non-transactional')})
    }

    EMAIL_BACKEND = 'django_email_multibackend.backends.EmailMultiServerBackend'


With this setting 70% of emails will be sent via mailjet and 30% via mandrill; the mandrill backend will never be used to send emails with header 
X-MAIL-TYPE=non-transactional


Email Routing Conditions
========================

Routing conditions must be callables classes (or callable factories), accept one argument (the email message is sent at routing time) and finally return a boolean see `django_email_multibackend.conditions.BaseCondition` and other implementations.

Conditions are initialised with the options provided in the EMAIL\_BACKENDS\_CONDITIONS settings and then called with the email message to send as parameter.


Tests
=====

You can run tests via setuptools (it will install the requirements to run the tests)    

` python setup.py test `

if you want to skip the setuptools  

` python runtests.py `

or just use py.test directly    

` DJANGO_SETTINGS_MODULE='django_email_multibackend.test_settings' py.test django_email_multibackend `

Every build of the project is built on Travis CI against python 2.5 / 2.6 / 2.7
