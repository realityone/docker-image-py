from . import digest as digest_
from . import regexp

ImageRegexps = regexp.ImageRegexps

NAME_TOTAL_LENGTH_MAX = 255
DEFAULT_DOMAIN = 'docker.io'
LEGACY_DEFAULT_DOMAIN = 'index.docker.io'
OFFICIAL_REPO_NAME = 'library'
LOCALHOST = 'localhost'
INVALID_REF_CHARS_TABLE = {ord(i): None for i in "?[]{}~!#$%^&*()+|<>,'\""}

class InvalidReference(Exception):
    @classmethod
    def default(cls):
        return cls("invalid reference")


class ReferenceInvalidFormat(InvalidReference):
    @classmethod
    def default(cls):
        return cls("invalid reference format")


class TagInvalidFormat(InvalidReference):
    @classmethod
    def default(cls):
        return cls("invalid tag format")


class DigestInvalidFormat(InvalidReference):
    @classmethod
    def default(cls):
        return cls("invalid digest format")


class NameEmpty(InvalidReference):
    @classmethod
    def default(cls):
        return cls("repository name must have at least one component")


class NameTooLong(InvalidReference):
    @classmethod
    def default(cls):
        return cls("repository name must not be more than {} characters".format(NAME_TOTAL_LENGTH_MAX))


class NameContainsUppercase(InvalidReference):
    @classmethod
    def default(cls):
        return cls("repository name must be lowercase")


class ReferenceHasNoName(InvalidReference):
    pass


class NameNotCanonical(InvalidReference):
    @classmethod
    def default(cls):
        return cls("repository name must be canonical")


class Repository(dict):
    def __init__(self, domain, path):
        self['domain'] = domain
        self['path'] = path
        super(Repository, self).__init__()

    def string(self):
        return self.name()

    def name(self):
        if not self['domain']:
            return self['path']
        return self['domain'] + '/' + self['path']


class Reference(dict):
    def __init__(self, name=None, tag=None, digest=None):
        super(Reference, self).__init__()
        self['name'] = name
        self['tag'] = tag
        self['digest'] = digest
        self.repository = Repository(*self.split_hostname())

    def split_hostname(self):
        """Split this already-parsed reference into raw domain and path parts.

        This mirrors github.com/distribution/reference's raw splitDomain logic:
        it uses the reference grammar captures directly and does not apply
        Docker Hub familiar-name normalization. As a result, a syntactically
        valid two-component name such as "containous/traefik" is split as
        ("containous", "traefik").

        Use parse_normalized_named() before calling split_hostname() when the
        caller wants Docker CLI style behavior, where "containous/traefik"
        becomes "docker.io/containous/traefik".
        """
        name = self['name']
        matched = ImageRegexps.ANCHORED_NAME_REGEXP.match(name)
        if not matched:
            return '', name
        matches = matched.groups()
        if len(matches) != 2:
            return '', name
        return matches[0], matches[1]

    def string(self):
        return '{}:{}@{}'.format(self['name'], self['tag'], self['digest'])

    def best_reference(self):
        if not self['name']:
            if self['digest']:
                return DigestReference(self['digest'])
            return None

        if not self['tag']:
            if self['digest']:
                return CanonicalReference(self['name'], self['digest'])
            return NamedReference(self['name'])

        if not self['digest']:
            return TaggedReference(self['name'], self['tag'])

        return self

    @classmethod
    def try_validate(cls, s):
        if not s:
            raise NameEmpty.default()
        if '/' not in s:
            return
        hostname, _ = s.split('/', 1)
        if '.' not in hostname:
            return
        if s.translate(INVALID_REF_CHARS_TABLE) != s:
            raise ReferenceInvalidFormat.default()
        matched = ImageRegexps.ANCHORED_HOSTNAME_REGEXP.match(hostname)
        if not matched:
            raise ReferenceInvalidFormat.default()

    @classmethod
    def parse(cls, s):
        """Parse a syntactically valid Docker image reference.

        This is the raw parser, matching github.com/distribution/reference.Parse.
        It validates and captures the input according to the reference grammar,
        then returns the most specific Reference subtype for the provided name,
        tag, and digest.

        It intentionally does not infer default Docker Hub domains or the
        "library/" namespace. For example, "containous/traefik" is parsed as a
        raw name whose domain capture is "containous" and path capture is
        "traefik". Use parse_normalized_named() for Docker familiar-name
        normalization.
        """
        cls.try_validate(s)

        matched = ImageRegexps.REFERENCE_REGEXP.match(s)
        if not matched:
            if ImageRegexps.REFERENCE_REGEXP.match(s.lower()):
                raise NameContainsUppercase.default()
            raise ReferenceInvalidFormat.default()

        matches = matched.groups()
        ref = cls(name=matches[0], tag=matches[1])
        if len(ref.repository['path']) > NAME_TOTAL_LENGTH_MAX:
            raise NameTooLong.default()

        if matches[2]:
            digest_.validate_digest(matches[2])
            ref['digest'] = matches[2]

        r = ref.best_reference()
        if not r:
            raise NameEmpty.default()

        return r

    @staticmethod
    def _contains_any(s, chars):
        for c in chars:
            if c in s:
                return True
        return False

    @classmethod
    def split_docker_domain(cls, name):
        """Split a familiar Docker name into canonical domain and remote name.

        This mirrors github.com/distribution/reference's splitDockerDomain
        helper. It applies Docker's heuristic for deciding whether the first
        path component is a registry domain:

        * "localhost" is always a domain.
        * "index.docker.io" is canonicalized to "docker.io".
        * components containing "." or ":" are treated as domains.
        * uppercase first components are treated as domains because repository
          namespaces must be lowercase.
        * otherwise, the default Docker Hub domain is used and the whole input
          remains the remote name.

        Single-component Docker Hub names also receive the "library/" prefix.
        """
        maybe_domain, sep, maybe_remote_name = name.partition('/')
        if not sep:
            return DEFAULT_DOMAIN, OFFICIAL_REPO_NAME + '/' + name

        if maybe_domain == LOCALHOST:
            domain, remainder = maybe_domain, maybe_remote_name
        elif maybe_domain == LEGACY_DEFAULT_DOMAIN:
            domain, remainder = DEFAULT_DOMAIN, maybe_remote_name
        elif cls._contains_any(maybe_domain, '.:'):
            domain, remainder = maybe_domain, maybe_remote_name
        elif maybe_domain.lower() != maybe_domain:
            domain, remainder = maybe_domain, maybe_remote_name
        else:
            domain, remainder = DEFAULT_DOMAIN, name

        if domain == LEGACY_DEFAULT_DOMAIN:
            domain = DEFAULT_DOMAIN
        if domain == DEFAULT_DOMAIN and '/' not in remainder:
            remainder = OFFICIAL_REPO_NAME + '/' + remainder
        return domain, remainder

    @classmethod
    def parse_normalized_named(cls, s):
        """Parse a named reference using Docker familiar-name normalization.

        This mirrors github.com/distribution/reference.ParseNormalizedNamed.
        It first rewrites familiar Docker names with split_docker_domain(), then
        parses the canonical result with parse(). Examples:

        * "ubuntu" becomes "docker.io/library/ubuntu".
        * "containous/traefik" becomes "docker.io/containous/traefik".
        * "example.com/repo" keeps "example.com" as the domain.

        Use this method, not parse(), when user input should behave like Docker
        CLI image names.
        """
        cls.try_validate(s)

        matched = ImageRegexps.ANCHORED_IDENTIFIER_REGEXP.match(s)
        if matched:
            raise InvalidReference("invalid repository name (%s), cannot specify 64-byte hexadecimal strings" % s)
        domain, remainder = cls.split_docker_domain(s)
        remote_name = remainder
        tag_sep = remainder.find(':')
        if tag_sep > -1:
            remote_name = remainder[:tag_sep]
        if remote_name.lower() != remote_name:
            raise InvalidReference("invalid reference format: repository name (%s) must be lowercase" % remote_name)

        ref = cls.parse(domain + '/' + remainder)
        if not ref['name']:
            raise ReferenceHasNoName("reference %s has no name", ref.string())
        return ref

    @classmethod
    def parse_named(cls, s):
        named = cls.parse_normalized_named(s)
        if named.string() != s:
            raise NameNotCanonical.default()
        return named

    def domain(self):
        return self.repository['domain']

    def path(self):
        return self.repository['path']

    def familiar(self):
        repo = Repository(**self.repository.copy())
        if repo['domain'] == DEFAULT_DOMAIN:
            repo['domain'] = ''
            split = repo['path'].split('/')
            if len(split) == 2 and split[0] == OFFICIAL_REPO_NAME:
                repo['path'] = split[1]
        return self.parse(repo.string())

    def familiar_name(self):
        return self.familiar().string()


class NamedReference(Reference):
    def __init__(self, name, **kwargs):
        super(NamedReference, self).__init__(name=name, **kwargs)

    def string(self):
        return '{}'.format(self['name'])


class DigestReference(Reference):
    def __init__(self, digest, **kwargs):
        super(DigestReference, self).__init__(digest=digest, **kwargs)

    def string(self):
        return self['digest']


class CanonicalReference(NamedReference):
    def __init__(self, name, digest, **kwargs):
        super(CanonicalReference, self).__init__(name=name, digest=digest, **kwargs)

    def string(self):
        return '{}@{}'.format(self['name'], self['digest'])


class TaggedReference(NamedReference):
    def __init__(self, name, tag, **kwargs):
        super(TaggedReference, self).__init__(name=name, tag=tag, **kwargs)

    def string(self):
        return '{}:{}'.format(self['name'], self['tag'])
