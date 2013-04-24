import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
test_dir = os.path.join(current_dir, 'tests')

if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'django_email_multibackend.test_settings'
    DJANGO_SETTINGS_MODULE = 'django_email_multibackend.test_settings'


def runtests(args=None):
    import pytest
    sys.path.append(test_dir)
    result = pytest.main(['django_email_multibackend'])
    sys.exit(result)


if __name__ == '__main__':
    runtests(sys.argv)
