from django.conf import settings

DEFAULT_CONDITIONS = [
    ('django_email_multibackend.conditions.MatchAll', {})
]

EMAIL_BACKENDS_CONDITIONS = getattr(settings, 'EMAIL_BACKENDS_CONDITIONS', {})
EMAIL_BACKENDS_WEIGHTS = getattr(settings, 'EMAIL_BACKENDS_WEIGHTS', tuple())
EMAIL_BACKENDS = getattr(settings, 'EMAIL_BACKENDS', {})