from django.core.mail import EmailMessage


class BaseCondition(object):

    def __init__(self, **kwargs):
        self.params = kwargs

    def __call__(self, message):
        if not isinstance(message, (EmailMessage, )):
            raise TypeError('%r is not a subclass of django.core.mail.EmailMessage' % message)
        return self.check(message)

    def check(self, message):
        raise NotImplementedError

class MatchAll(BaseCondition):
    def check(self, message):
        return True

class MatchAny(BaseCondition):
    """
    >>> mail = EmailMessage()

    >>> mail.extra_headers['X-CAMPAIGN-NAME'] = 'weekly-mail'

    >>> MatchAny(\
    ('django_email_multibackend.conditions.FilterMailByHeader', {'header': ('X-CAMPAIGN-NAME', 'daily-mail')}),\
    ('django_email_multibackend.conditions.FilterMailByHeader', {'header': ('X-CAMPAIGN-NAME', 'weekly-mail')})\
    )(mail)
    True
    """
    def __init__(self, *conditions):
        from django_email_multibackend.backends import load_class
        self.conditions = []
        for condition in conditions:
            try:
                kls_name, params = condition
            except ValueError:
                kls_name, params = condition[0], {}
            self.conditions.append(load_class(kls_name)(**params))

    def check(self, message):
        for condition in self.conditions:
            if condition(message):
                return True
        return False

class FilterMailByHeader(BaseCondition):
    """
    Filter emails by headers

    >>> mail = EmailMessage()

    >>> mail.extra_headers['X-CAMPAIGN-NAME'] = 'weekly-mail'

    >>> FilterMailByHeader(header=('X-CAMPAIGN-NAME', 'weekly-mail'))(mail)
    True
    >>> FilterMailByHeader(header=('X-CAMPAIGN-NAME', 'daily-mail'))(mail)
    False
    >>> FilterMailByHeader(header=('X-TRANSACTION-ID', '999'))(mail)
    False
    """

    def check(self, message):
        unset = dict()
        header_name, header_value = self.params['header']
        mail_header_value = message.extra_headers.get(header_name, unset)
        return (not mail_header_value is unset) and (mail_header_value == header_value)

class ExcludeMailByHeader(FilterMailByHeader):
    """
    Exclude emails by headers

    >>> mail = EmailMessage()

    >>> mail.extra_headers['X-CAMPAIGN-NAME'] = 'weekly-mail'

    >>> ExcludeMailByHeader(header=('X-CAMPAIGN-NAME', 'weekly-mail'))(mail)
    False
    >>> ExcludeMailByHeader(header=('X-CAMPAIGN-NAME', 'daily-mail'))(mail)
    True
    >>> ExcludeMailByHeader(header=('X-TRANSACTION-ID', '999'))(mail)
    True
    """

    def check(self, message):
        return not super(ExcludeMailByHeader, self).check(message)

