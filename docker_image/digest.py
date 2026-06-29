from . import regexp

DigestRegexps = regexp.DigestRegexps


class InvalidDigest(Exception):
    @classmethod
    def default(cls):
        return cls("invalid digest")


class DigestUnsupported(InvalidDigest):
    @classmethod
    def default(cls):
        return cls("unsupported digest algorithm")


class DigestInvalidLength(InvalidDigest):
    @classmethod
    def default(cls):
        return cls("invalid checksum digest length")


DIGESTS_SIZE = {
    'sha256': 32,
    'sha384': 48,
    'sha512': 64,
}

LOWER_HEX_CHARS = frozenset('0123456789abcdef')


def validate_digest(digest):
    i = digest.find(':')
    # case: "sha256:" with no hex.
    if i < 0 or ((i + 1) == len(digest)):
        raise InvalidDigest.default()

    algorithm = digest[:i]
    if algorithm not in DIGESTS_SIZE:
        matched = DigestRegexps.DIGEST_REGEXP_ANCHORED.match(digest)
        if not matched:
            raise InvalidDigest.default()
        raise DigestUnsupported.default()

    encoded = digest[i + 1:]
    if DIGESTS_SIZE[algorithm] * 2 != len(encoded):
        raise DigestInvalidLength.default()

    if any(c not in LOWER_HEX_CHARS for c in encoded):
        raise InvalidDigest.default()
