import unittest

from docker_image import regexp


# Expected patterns were generated from github.com/distribution/reference/regexp.go
# by expanding its Go string expressions. Keep them as literals so this test
# does not duplicate docker_image.regexp's construction helpers.
ALPHA_NUMERIC = r'[a-z0-9]+'
SEPARATOR = r'(?:[._]|__|[-]+)'
LOCALHOST = r'localhost'
DOMAIN_NAME_COMPONENT = r'(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9])'
OPTIONAL_PORT = r'(?::[0-9]+)?'
TAG = r'[\w][\w.-]{0,127}'
DIGEST_PAT = r'[A-Za-z][A-Za-z0-9]*(?:[-_+.][A-Za-z][A-Za-z0-9]*)*[:][[:xdigit:]]{32,}'
IDENTIFIER = r'([a-f0-9]{64})'
IPV6_ADDRESS = r'\[(?:[a-fA-F0-9:]+)\]'
DOMAIN_NAME = r'(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9])(?:\.(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]))*'
HOST = r'(?:(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9])(?:\.(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]))*|\[(?:[a-fA-F0-9:]+)\])'
DOMAIN_AND_PORT = r'(?:(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9])(?:\.(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]))*|\[(?:[a-fA-F0-9:]+)\])(?::[0-9]+)?'
PATH_COMPONENT = r'[a-z0-9]+(?:(?:[._]|__|[-]+)[a-z0-9]+)*'
REMOTE_NAME = r'[a-z0-9]+(?:(?:[._]|__|[-]+)[a-z0-9]+)*(?:/[a-z0-9]+(?:(?:[._]|__|[-]+)[a-z0-9]+)*)*'
NAME_PAT = r'(?:(?:(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9])(?:\.(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]))*|\[(?:[a-fA-F0-9:]+)\])(?::[0-9]+)?/)?[a-z0-9]+(?:(?:[._]|__|[-]+)[a-z0-9]+)*(?:/[a-z0-9]+(?:(?:[._]|__|[-]+)[a-z0-9]+)*)*'
ANCHORED_TAG = r'^[\w][\w.-]{0,127}$'
ANCHORED_DIGEST_PAT = r'^[A-Za-z][A-Za-z0-9]*(?:[-_+.][A-Za-z][A-Za-z0-9]*)*[:][[:xdigit:]]{32,}$'
ANCHORED_NAME_PAT = r'^(?:((?:(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9])(?:\.(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]))*|\[(?:[a-fA-F0-9:]+)\])(?::[0-9]+)?)/)?([a-z0-9]+(?:(?:[._]|__|[-]+)[a-z0-9]+)*(?:/[a-z0-9]+(?:(?:[._]|__|[-]+)[a-z0-9]+)*)*)$'
REFERENCE_PAT = r'^((?:(?:(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9])(?:\.(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]))*|\[(?:[a-fA-F0-9:]+)\])(?::[0-9]+)?/)?[a-z0-9]+(?:(?:[._]|__|[-]+)[a-z0-9]+)*(?:/[a-z0-9]+(?:(?:[._]|__|[-]+)[a-z0-9]+)*)*)(?::([\w][\w.-]{0,127}))?(?:@([A-Za-z][A-Za-z0-9]*(?:[-_+.][A-Za-z][A-Za-z0-9]*)*[:][[:xdigit:]]{32,}))?$'
ANCHORED_IDENTIFIER = r'^([a-f0-9]{64})$'

# Mirrors github.com/opencontainers/go-digest.DigestRegexp.
DIGEST_REGEXP_PATTERN = r'[a-z0-9]+(?:[.+_-][a-z0-9]+)*:[a-zA-Z0-9=_-]+'
ANCHORED_DIGEST_REGEXP_PATTERN = r'^[a-z0-9]+(?:[.+_-][a-z0-9]+)*:[a-zA-Z0-9=_-]+$'


def check_regexp(test_case, compiled, input_, should_match, subs=None):
    subs = subs or []
    matched = compiled.match(input_)

    if should_match and matched:
        test_case.assertEqual(input_, matched.group(0))
        actual_subs = [value if value is not None else '' for value in matched.groups()]
        test_case.assertGreaterEqual(len(actual_subs), len(subs))
        test_case.assertEqual(subs, actual_subs[:len(subs)])
    elif should_match:
        test_case.fail('Expected match for {!r}'.format(input_))
    elif matched:
        test_case.fail('Unexpected match for {!r}'.format(input_))


class TestRegexp(unittest.TestCase):
    def test_patterns_borrowed_from_go_reference(self):
        image_regexps = regexp.ImageRegexps

        test_cases = [
            ('ALPHA_NUMERIC', ALPHA_NUMERIC, regexp.ALPHA_NUMERIC, image_regexps.ALPHA_NUMERIC_REGEXP.pattern),
            ('SEPARATOR', SEPARATOR, regexp.SEPARATOR, image_regexps.SEPARATOR_REGEXP.pattern),
            ('LOCALHOST', LOCALHOST, regexp.LOCALHOST),
            ('DOMAIN_NAME_COMPONENT', DOMAIN_NAME_COMPONENT, regexp.DOMAIN_NAME_COMPONENT,
             image_regexps.HOSTNAME_COMPONENT_REGEXP.pattern),
            ('OPTIONAL_PORT', OPTIONAL_PORT, regexp.OPTIONAL_PORT, image_regexps.OPTIONAL_PORT_REGEXP.pattern),
            ('TAG', TAG, regexp.TAG, image_regexps.TAG_REGEXP.pattern),
            ('DIGEST_PAT', DIGEST_PAT, regexp.DIGEST_PAT, image_regexps.DIGEST_REGEXP.pattern),
            ('IDENTIFIER', IDENTIFIER, regexp.IDENTIFIER, image_regexps.IDENTIFIER_REGEXP.pattern),
            ('IPV6_ADDRESS', IPV6_ADDRESS, regexp.IPV6_ADDRESS, image_regexps.IPV6_ADDRESS_REGEXP.pattern),
            ('DOMAIN_NAME', DOMAIN_NAME, regexp.DOMAIN_NAME, image_regexps.DOMAIN_NAME_REGEXP.pattern),
            ('HOST', HOST, regexp.HOST, image_regexps.HOST_REGEXP.pattern),
            ('DOMAIN_AND_PORT', DOMAIN_AND_PORT, regexp.DOMAIN_AND_PORT, image_regexps.HOSTNAME_REGEXP.pattern),
            ('PATH_COMPONENT', PATH_COMPONENT, regexp.PATH_COMPONENT, image_regexps.NAME_COMPONENT_REGEXP.pattern),
            ('REMOTE_NAME', REMOTE_NAME, regexp.REMOTE_NAME, image_regexps.REMOTE_NAME_REGEXP.pattern),
            ('NAME_PAT', NAME_PAT, regexp.NAME_PAT, image_regexps.NAME_REGEXP.pattern),
            ('ANCHORED_TAG', ANCHORED_TAG, image_regexps.ANCHORED_TAG_REGEXP.pattern),
            ('ANCHORED_DIGEST_PAT', ANCHORED_DIGEST_PAT, image_regexps.ANCHORED_DIGEST_REGEXP.pattern),
            ('ANCHORED_NAME_PAT', ANCHORED_NAME_PAT, regexp.ANCHORED_NAME_PAT,
             image_regexps.ANCHORED_NAME_REGEXP.pattern),
            ('REFERENCE_PAT', REFERENCE_PAT, regexp.REFERENCE_PAT, image_regexps.REFERENCE_REGEXP.pattern),
            ('ANCHORED_IDENTIFIER', ANCHORED_IDENTIFIER, image_regexps.ANCHORED_IDENTIFIER_REGEXP.pattern),
            ('DIGEST_REGEXP_PATTERN', DIGEST_REGEXP_PATTERN, regexp.DIGEST_REGEXP_PATTERN,
             regexp.DigestRegexps.DIGEST_REGEXP.pattern),
            ('ANCHORED_DIGEST_REGEXP_PATTERN', ANCHORED_DIGEST_REGEXP_PATTERN,
             regexp.DigestRegexps.DIGEST_REGEXP_ANCHORED.pattern),
        ]

        for name, expected, *actuals in test_cases:
            with self.subTest(pattern=name):
                for actual in actuals:
                    self.assertEqual(expected, actual)

    def test_domain_regexp_cases_from_go_reference(self):
        test_cases = [
            ('test.com', True),
            ('test.com:10304', True),
            ('test.com:http', False),
            ('localhost', True),
            ('localhost:8080', True),
            ('a', True),
            ('a.b', True),
            ('ab.cd.com', True),
            ('a-b.com', True),
            ('-ab.com', False),
            ('ab-.com', False),
            ('ab.c-om', True),
            ('ab.-com', False),
            ('ab.com-', False),
            ('0101.com', True),
            ('001a.com', True),
            ('b.gbc.io:443', True),
            ('b.gbc.io', True),
            ('xn--n3h.com', True),
            ('Asdf.com', True),
            ('192.168.1.1:75050', True),
            ('192.168.1.1:750050', True),
            ('[fd00:1:2::3]:75050', True),
            ('[fd00:1:2::3]75050', False),
            ('[fd00:1:2::3]::75050', False),
            ('[fd00:1:2::3%eth0]:75050', False),
            ('[fd00123123123]:75050', True),
            ('[2001:0db8:85a3:0000:0000:8a2e:0370:7334]:75050', True),
            ('[2001:0db8:85a3:0000:0000:8a2e:0370:7334]:750505', True),
            ('fd00:1:2::3:75050', False),
        ]

        for input_, should_match in test_cases:
            check_regexp(self, regexp.ImageRegexps.ANCHORED_DOMAIN_REGEXP, input_, should_match)

    def test_tag_regexp_cases_from_go_reference(self):
        test_cases = [
            ('latest', True),
            ('A.B_c-1', True),
            ('ɰoo', False),
            ('éoo', False),
        ]

        for input_, should_match in test_cases:
            check_regexp(self, regexp.ImageRegexps.ANCHORED_TAG_REGEXP, input_, should_match)

    def test_full_name_regexp_cases_from_go_reference(self):
        self.assertEqual(2, regexp.ImageRegexps.ANCHORED_NAME_REGEXP.groups)

        test_cases = [
            ('', False, []),
            ('short', True, ['', 'short']),
            ('simple/name', True, ['simple', 'name']),
            ('library/ubuntu', True, ['library', 'ubuntu']),
            ('docker/stevvooe/app', True, ['docker', 'stevvooe/app']),
            ('aa/aa/aa/aa/aa/aa/aa/aa/aa/bb/bb/bb/bb/bb/bb', True,
             ['aa', 'aa/aa/aa/aa/aa/aa/aa/aa/bb/bb/bb/bb/bb/bb']),
            ('aa/aa/bb/bb/bb', True, ['aa', 'aa/bb/bb/bb']),
            ('a/a/a/a', True, ['a', 'a/a/a']),
            ('a/a/a/a/', False, []),
            ('a//a/a', False, []),
            ('a', True, ['', 'a']),
            ('a/aa', True, ['a', 'aa']),
            ('a/aa/a', True, ['a', 'aa/a']),
            ('foo.com', True, ['', 'foo.com']),
            ('foo.com/', False, []),
            ('foo.com:8080/bar', True, ['foo.com:8080', 'bar']),
            ('foo.com:http/bar', False, []),
            ('foo.com/bar', True, ['foo.com', 'bar']),
            ('foo.com/bar/baz', True, ['foo.com', 'bar/baz']),
            ('localhost:8080/bar', True, ['localhost:8080', 'bar']),
            ('sub-dom1.foo.com/bar/baz/quux', True, ['sub-dom1.foo.com', 'bar/baz/quux']),
            ('blog.foo.com/bar/baz', True, ['blog.foo.com', 'bar/baz']),
            ('a^a', False, []),
            ('aa/asdf$$^/aa', False, []),
            ('asdf$$^/aa', False, []),
            ('aa-a/a', True, ['aa-a', 'a']),
            ('a/' * 128 + 'a', True, ['a', 'a/' * 127 + 'a']),
            ('a-/a/a/a', False, []),
            ('foo.com/a-/a/a', False, []),
            ('-foo/bar', False, []),
            ('foo/bar-', False, []),
            ('foo-/bar', False, []),
            ('foo/-bar', False, []),
            ('_foo/bar', False, []),
            ('foo_bar', True, ['', 'foo_bar']),
            ('foo_bar.com', True, ['', 'foo_bar.com']),
            ('foo_bar.com:8080', False, []),
            ('foo_bar.com:8080/app', False, []),
            ('foo.com/foo_bar', True, ['foo.com', 'foo_bar']),
            ('____/____', False, []),
            ('_docker/_docker', False, []),
            ('docker_/docker_', False, []),
            ('b.gcr.io/test.example.com/my-app', True, ['b.gcr.io', 'test.example.com/my-app']),
            ('xn--n3h.com/myimage', True, ['xn--n3h.com', 'myimage']),
            ('xn--7o8h.com/myimage', True, ['xn--7o8h.com', 'myimage']),
            ('example.com/xn--7o8h.com/myimage', True, ['example.com', 'xn--7o8h.com/myimage']),
            ('example.com/some_separator__underscore/myimage', True,
             ['example.com', 'some_separator__underscore/myimage']),
            ('example.com/__underscore/myimage', False, []),
            ('example.com/..dots/myimage', False, []),
            ('example.com/.dots/myimage', False, []),
            ('example.com/nodouble..dots/myimage', False, []),
            ('docker./docker', False, []),
            ('.docker/docker', False, []),
            ('docker-/docker', False, []),
            ('-docker/docker', False, []),
            ('do..cker/docker', False, []),
            ('do__cker:8080/docker', False, []),
            ('do__cker/docker', True, ['', 'do__cker/docker']),
            ('registry.io/foo/project--id.module--name.ver---sion--name', True,
             ['registry.io', 'foo/project--id.module--name.ver---sion--name']),
            ('Asdf.com/foo/bar', True, ['Asdf.com', 'foo/bar']),
            ('Foo/FarB', False, []),
        ]

        for input_, should_match, subs in test_cases:
            check_regexp(self, regexp.ImageRegexps.ANCHORED_NAME_REGEXP, input_, should_match, subs)

    def test_reference_regexp_cases_from_go_reference(self):
        self.assertEqual(3, regexp.ImageRegexps.REFERENCE_REGEXP.groups)

        valid_digest = 'sha256:be178c0543eb17f5f3043021c9e5fcf30285e557a4fc309cce97ff9ca6182912'
        test_cases = [
            ('registry.com:8080/myapp:tag', True, ['registry.com:8080/myapp', 'tag', '']),
            ('registry.com:8080/myapp@{}'.format(valid_digest), True,
             ['registry.com:8080/myapp', '', valid_digest]),
            ('registry.com:8080/myapp:tag2@{}'.format(valid_digest), True,
             ['registry.com:8080/myapp', 'tag2', valid_digest]),
            ('registry.com:8080/myapp@sha256:badbadbadbad', False, []),
            ('registry.com:8080/myapp:invalid~tag', False, []),
            ('bad_hostname.com:8080/myapp:tag', False, []),
            ('localhost:8080@{}'.format(valid_digest), True, ['localhost', '8080', valid_digest]),
            ('localhost:8080/name@{}'.format(valid_digest), True, ['localhost:8080/name', '', valid_digest]),
            ('localhost:http/name@{}'.format(valid_digest), False, []),
            ('localhost@{}'.format(valid_digest), True, ['localhost', '', valid_digest]),
            ('registry.com:8080/myapp@bad', False, []),
            ('registry.com:8080/myapp@2bad', False, []),
        ]

        for input_, should_match, subs in test_cases:
            check_regexp(self, regexp.ImageRegexps.REFERENCE_REGEXP, input_, should_match, subs)

    def test_identifier_regexp_cases_from_go_reference(self):
        test_cases = [
            ('da304e823d8ca2b9d863a3c897baeb852ba21ea9a9f1414736394ae7fcaf9821', True),
            ('7EC43B381E5AEFE6E04EFB0B3F0693FF2A4A50652D64AEC573905F2DB5889A1C', False),
            ('da304e823d8ca2b9d863a3c897baeb852ba21ea9a9f1414736394ae7fcaf', False),
            ('sha256:da304e823d8ca2b9d863a3c897baeb852ba21ea9a9f1414736394ae7fcaf9821', False),
            ('da304e823d8ca2b9d863a3c897baeb852ba21ea9a9f1414736394ae7fcaf98218482', False),
        ]

        for input_, should_match in test_cases:
            check_regexp(self, regexp.ImageRegexps.ANCHORED_IDENTIFIER_REGEXP, input_, should_match)
