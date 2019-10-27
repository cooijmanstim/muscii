import re

class HandlersByRegexKeyError(KeyError):
    pass

class HandlersByRegex(object):
    def __init__(self, *args, **kwargs):
        self.dikt = {}
        for regex_like, handler in dict(*args, **kwargs).iteritems():
            if isinstance(regex_like, tuple):
                regex = re.compile(*regex_like)
            elif isinstance(regex_like, basestring):
                regex = re.compile(regex_like)
            else:
                regex = regex_like
            self.dikt[regex] = handler

    def __getitem__(self, string):
        for key, handler in self.dikt.iteritems():
            match = key.search(string)
            if match:
                return handler(**match.groupdict())
        else:
            raise KeyError()

    def get(self, string, default=None):
        try:
            return self[string]
        except KeyError:
            return default

class DefaultEqualityMixin(object):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))
