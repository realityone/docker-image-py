import regex


def optional(*res):
    return r'(?:{})?'.format(''.join(res))


def any_times(*res):
    return r'(?:{})*'.format(''.join(res))


def capture(*res):
    return r'({})'.format(''.join(res))


def anchored(*res):
    return r'^{}$'.format(''.join(res))


def match(regexp):
    # Go regexp's Perl character classes are ASCII-only. Compile with ASCII
    # semantics so borrowed patterns like `\w` reject non-ASCII tag characters.
    return regex.compile(regexp, regex.ASCII)


# Base patterns mirror github.com/distribution/reference/regexp.go.
ALPHA_NUMERIC = r'[a-z0-9]+'
SEPARATOR = r'(?:[._]|__|[-]+)'
LOCALHOST = r'localhost'
DOMAIN_NAME_COMPONENT = r'(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9])'
OPTIONAL_PORT = r'(?::[0-9]+)?'
TAG = r'[\w][\w.-]{0,127}'
DIGEST_PAT = r'[A-Za-z][A-Za-z0-9]*(?:[-_+.][A-Za-z][A-Za-z0-9]*)*[:][[:xdigit:]]{32,}'
IDENTIFIER = r'([a-f0-9]{64})'
IPV6_ADDRESS = r'\[(?:[a-fA-F0-9:]+)\]'

DOMAIN_NAME = DOMAIN_NAME_COMPONENT + any_times(r'\.' + DOMAIN_NAME_COMPONENT)
HOST = r'(?:' + DOMAIN_NAME + r'|' + IPV6_ADDRESS + r')'
DOMAIN_AND_PORT = HOST + OPTIONAL_PORT
PATH_COMPONENT = ALPHA_NUMERIC + any_times(SEPARATOR + ALPHA_NUMERIC)
REMOTE_NAME = PATH_COMPONENT + any_times(r'/' + PATH_COMPONENT)
NAME_PAT = optional(DOMAIN_AND_PORT + r'/') + REMOTE_NAME
REFERENCE_PAT = anchored(capture(NAME_PAT), optional(r':', capture(TAG)), optional(r'@', capture(DIGEST_PAT)))
ANCHORED_NAME_PAT = anchored(optional(capture(DOMAIN_AND_PORT), r'/'), capture(REMOTE_NAME))

# Mirrors github.com/opencontainers/go-digest.DigestRegexp.
DIGEST_REGEXP_PATTERN = r'[a-z0-9]+(?:[.+_-][a-z0-9]+)*:[a-zA-Z0-9=_-]+'


class ImageRegexps(object):
    ALPHA_NUMERIC_REGEXP = match(ALPHA_NUMERIC)
    SEPARATOR_REGEXP = match(SEPARATOR)
    NAME_COMPONENT_REGEXP = match(PATH_COMPONENT)
    HOSTNAME_COMPONENT_REGEXP = match(DOMAIN_NAME_COMPONENT)
    DOMAIN_NAME_REGEXP = match(DOMAIN_NAME)
    IPV6_ADDRESS_REGEXP = match(IPV6_ADDRESS)
    HOST_REGEXP = match(HOST)
    OPTIONAL_PORT_REGEXP = match(OPTIONAL_PORT)
    HOSTNAME_REGEXP = match(DOMAIN_AND_PORT)
    DOMAIN_REGEXP = HOSTNAME_REGEXP
    ANCHORED_HOSTNAME_REGEXP = match(anchored(DOMAIN_AND_PORT))
    ANCHORED_DOMAIN_REGEXP = ANCHORED_HOSTNAME_REGEXP
    TAG_REGEXP = match(TAG)
    ANCHORED_TAG_REGEXP = match(anchored(TAG))
    DIGEST_REGEXP = match(DIGEST_PAT)
    ANCHORED_DIGEST_REGEXP = match(anchored(DIGEST_PAT))
    REMOTE_NAME_REGEXP = match(REMOTE_NAME)
    NAME_REGEXP = match(NAME_PAT)
    ANCHORED_NAME_REGEXP = match(ANCHORED_NAME_PAT)
    REFERENCE_REGEXP = match(REFERENCE_PAT)
    IDENTIFIER_REGEXP = match(IDENTIFIER)
    ANCHORED_IDENTIFIER_REGEXP = match(anchored(IDENTIFIER))


class DigestRegexps(object):
    DIGEST_REGEXP = match(DIGEST_REGEXP_PATTERN)
    DIGEST_REGEXP_ANCHORED = match(anchored(DIGEST_REGEXP_PATTERN))
