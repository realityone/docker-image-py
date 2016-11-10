from . import regexp

ImageRegexps = regexp.ImageRegexps

NAME_TOTAL_LENGTH_MAX = 255


class ReferenceError(Exception):
    @classmethod
    def default(cls):
        return cls("reference error")


class ReferenceInvalidFormat(ReferenceError):
    @classmethod
    def default(cls):
        return cls("invalid reference format")


class TagInvalidFormat(ReferenceError):
    @classmethod
    def default(cls):
        return cls("invalid tag format")


class DigestInvalidFormat(ReferenceError):
    @classmethod
    def default(cls):
        return cls("invalid digest format")


class NameEmpty(ReferenceError):
    @classmethod
    def default(cls):
        return cls("repository name must have at least one component")


class NameTooLong(ReferenceError):
    @classmethod
    def default(cls):
        return cls("repository name must not be more than {} characters".format(NAME_TOTAL_LENGTH_MAX))


class Reference(dict):
    def __init__(self, name, tag=None, digest=None):
        super(Reference, self).__init__()
        self['name'] = name
        self['tag'] = tag
        self['digest'] = digest

    def string(self):
        return '{}:{}@{}'.format(self['name'], self['tag'], self['digest'])

    def best_reference(self):
        if not self['name']:
            if not self['digest']:
                return self['digest']
            return None

        if not self['tag']:
            if self['digest']:
                return CanonicalReference(self['name'], self['digest'])
            return NameReference(self['name'])

        if not self['digest']:
            return TaggedReference(self['name'], self['tag'])

    @classmethod
    def parse(cls, s):
        matched = ImageRegexps.REFERENCE_REGEXP.match(s)
        if not matched and not s:
            raise NameEmpty.default()
        if not matched:
            raise ReferenceInvalidFormat.default()

        matches = matched.groups()
        if len(matches[0]) > NAME_TOTAL_LENGTH_MAX:
            raise NameTooLong.default()

        ref = Reference(matches[0], tag=matches[1])
        if matches[2]:
            # validate digest
            ref['digest'] = matches[2]

        r = ref.best_reference()
        if not r:
            raise NameEmpty.default()

        return r


class CanonicalReference(Reference):
    def __init__(self, name, digest):
        super(CanonicalReference, self).__init__(name, digest=digest)

    def string(self):
        return '{}@{}'.format(self['name'], self['digest'])


class NameReference(Reference):
    def __init__(self, name):
        super(NameReference, self).__init__(name)

    def string(self):
        return '{}'.format(self['name'])


class TaggedReference(Reference):
    def __init__(self, name, tag):
        super(TaggedReference, self).__init__(name, tag=tag)

    def string(self):
        return '{}:{}'.format(self['name'], self['tag'])
