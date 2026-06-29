import unittest

from docker_image import reference


class TestParseRegressions(unittest.TestCase):
    def test_issue_invalid_reference_fast_failures(self):
        test_cases = [
            '123.dkr.ecr.eu-west-1.amazonaws.com:lol/abc:d',
            'docker.artifactory.us.foo.mycompany.com/bar/node?18',
        ]

        for input_ in test_cases:
            self.assertRaises(reference.ReferenceInvalidFormat, reference.Reference.parse, input_)

    def test_issue_5_docker_hub_namespace_normalization(self):
        ref = reference.Reference.parse_normalized_named('containous/traefik')

        self.assertEqual(('docker.io', 'containous/traefik'), ref.split_hostname())
        self.assertEqual('docker.io/containous/traefik', ref.string())
        self.assertEqual('docker.io', ref.domain())
        self.assertEqual('containous/traefik', ref.path())
        self.assertEqual('containous/traefik', ref.familiar_name())

    def test_issue_11_non_ascii_tags_are_rejected(self):
        test_cases = [
            'yay:ɰoo',
            'yay:éoo',
        ]

        for input_ in test_cases:
            self.assertRaises(reference.ReferenceInvalidFormat, reference.Reference.parse, input_)

    def test_issue_12_invalid_tag_characters_fail_fast(self):
        name = 'abcdefghijklmnopqrst'
        test_cases = [
            '[',
            ']',
            '$',
            '(',
            ')',
            '`',
            '&',
            '|',
            '<',
            '>',
            ';',
            ',',
            '\n',
            '{',
            '}',
            "'",
            '"',
        ]

        for char in test_cases:
            input_ = '{}:0.15{}.0'.format(name, char)
            self.assertRaises(reference.ReferenceInvalidFormat, reference.Reference.parse_normalized_named, input_)


class TestNormalize(unittest.TestCase):
    def test_parse_repository_info(self):
        def create_test_case(remote_name, familiar_name, full_name, ambiguous_name, domain):
            return {
                'remote_name': remote_name,
                'familiar_name': familiar_name,
                'full_name': full_name,
                'ambiguous_name': ambiguous_name,
                'domain': domain,
            }

        test_cases = [
            create_test_case('fooo', 'localhost/fooo', 'localhost/fooo', 'localhost/fooo', 'localhost'),
            create_test_case('fooo/bar', 'localhost/fooo/bar', 'localhost/fooo/bar', 'localhost/fooo/bar', 'localhost'),
            create_test_case('fooo', 'LOCALDOMAIN/fooo', 'LOCALDOMAIN/fooo', 'LOCALDOMAIN/fooo', 'LOCALDOMAIN'),
            create_test_case('fooo/bar', 'LOCALDOMAIN/fooo/bar', 'LOCALDOMAIN/fooo/bar', 'LOCALDOMAIN/fooo/bar',
                             'LOCALDOMAIN'),
            create_test_case('fooo/bar', 'fooo/bar', 'docker.io/fooo/bar', 'index.docker.io/fooo/bar', 'docker.io'),
            create_test_case('library/ubuntu', 'ubuntu', 'docker.io/library/ubuntu', 'library/ubuntu', 'docker.io'),
            create_test_case('nonlibrary/ubuntu', 'nonlibrary/ubuntu', 'docker.io/nonlibrary/ubuntu', '', 'docker.io'),
            create_test_case('other/library', 'other/library', 'docker.io/other/library', '', 'docker.io'),
            create_test_case('private/moonbase', '127.0.0.1:8000/private/moonbase', '127.0.0.1:8000/private/moonbase', '',
                             '127.0.0.1:8000'),
            create_test_case('privatebase', '127.0.0.1:8000/privatebase', '127.0.0.1:8000/privatebase', '',
                             '127.0.0.1:8000'),
            create_test_case('private/moonbase', 'example.com/private/moonbase', 'example.com/private/moonbase', '',
                             'example.com'),
            create_test_case('privatebase', 'example.com/privatebase', 'example.com/privatebase', '', 'example.com'),
            create_test_case('private/moonbase', 'example.com:8000/private/moonbase', 'example.com:8000/private/moonbase',
                             '', 'example.com:8000'),
            create_test_case('privatebasee', 'example.com:8000/privatebasee', 'example.com:8000/privatebasee', '',
                             'example.com:8000'),
            create_test_case('repo', '[2001:db8::1]/repo', '[2001:db8::1]/repo', '',
                             '[2001:db8::1]'),
            create_test_case('repo', '[2001:db8::1]:5000/repo', '[2001:db8::1]:5000/repo', '',
                             '[2001:db8::1]:5000'),
            create_test_case('foo', 'MyRegistry/foo', 'MyRegistry/foo', '',
                             'MyRegistry'),
            create_test_case('library/ubuntu-12.04-base', 'ubuntu-12.04-base', 'docker.io/library/ubuntu-12.04-base',
                             'index.docker.io/library/ubuntu-12.04-base', 'docker.io'),
            create_test_case('library/foo', 'foo', 'docker.io/library/foo', 'docker.io/foo', 'docker.io'),
            create_test_case('library/foo/bar', 'library/foo/bar', 'docker.io/library/foo/bar', '', 'docker.io'),
            create_test_case('store/foo/bar', 'store/foo/bar', 'docker.io/store/foo/bar', '', 'docker.io'),
            create_test_case('bar', 'Foo/bar', 'Foo/bar', '', 'Foo'),
            create_test_case('bar', 'FOO/bar', 'FOO/bar', '', 'FOO'),
        ]
        for tc in test_cases:
            ref_strings = [tc['familiar_name'], tc['full_name']]
            if tc['ambiguous_name'] != '':
                ref_strings.append(tc['ambiguous_name'])

            refs = []
            for r in ref_strings:
                try:
                    named = reference.Reference.parse_normalized_named(r)
                except Exception as e:
                    raise e
                refs.append(named)

            for r in refs:
                self.assertEqual(tc['familiar_name'], r.familiar_name())
                self.assertEqual(tc['full_name'], r.string())
                self.assertEqual(tc['domain'], r.domain())
                self.assertEqual(tc['remote_name'], r.path())

    def test_validate_reference_name(self):
        valid_repo_names = [
            "docker/docker",
            "library/debian",
            "debian",
            "localhost/library/debian",
            "localhost/debian",
            "LOCALDOMAIN/library/debian",
            "LOCALDOMAIN/debian",
            "docker.io/docker/docker",
            "docker.io/library/debian",
            "docker.io/debian",
            "index.docker.io/docker/docker",
            "index.docker.io/library/debian",
            "index.docker.io/debian",
            "127.0.0.1:5000/docker/docker",
            "127.0.0.1:5000/library/debian",
            "127.0.0.1:5000/debian",
            "192.168.0.1",
            "192.168.0.1:80",
            "192.168.0.1:8/debian",
            "192.168.0.2:25000/debian",
            "[2001:db8::1]/debian",
            "[2001:db8::1]:5000/debian",
            "[fc00::1]:5000/docker",
            "[fc00::1]:5000/docker/docker",
            "[fc00:1:2:3:4:5:6:7]:5000/library/debian",
            "MyRegistry/foo",
            "thisisthesongthatneverendsitgoesonandonandonthisisthesongthatnev",

            # This test case was moved from invalid to valid since it is valid input
            # when specified with a hostname, it removes the ambiguity from about
            # whether the value is an identifier or repository name
            "docker.io/1a3f5e7d9c1b3a5f7e9d1c3b5a7f9e1d3c5b7a9f1e3d5d7c9b1a3f5e7d9c1b3a",
            "Docker/docker",
            "DOCKER/docker",
        ]
        invalid_repo_names = [
            "https://github.com/docker/docker",
            "docker/Docker",
            "-docker",
            "-docker/docker",
            "-docker.io/docker/docker",
            "docker///docker",
            "docker.io/docker/Docker",
            "docker.io/docker///docker",
            "[fc00::1]",
            "[fc00::1]:5000",
            "fc00::1:5000/debian",
            "[fe80::1%eth0]:5000/debian",
            "[2001:db8:3:4::192.0.2.33]:5000/debian",
            "1a3f5e7d9c1b3a5f7e9d1c3b5a7f9e1d3c5b7a9f1e3d5d7c9b1a3f5e7d9c1b3a",
            "[::ffff:192.168.0.1]/docker",
            "docker.artifactory.us.foo.mycompany.com/bar/node?18"
        ]
        for name in valid_repo_names:
            ref = reference.Reference.parse_normalized_named(name)
            self.assertIsNotNone(ref)

        for name in invalid_repo_names:
            self.assertRaises(reference.InvalidReference, reference.Reference.parse_normalized_named, name)

    def test_validate_remote_name(self):
        valid_repository_names = [
            # Sanity check.
            "docker/docker",

            # Allow 64-character non-hexadecimal names (hexadecimal names are forbidden).
            "thisisthesongthatneverendsitgoesonandonandonthisisthesongthatnev",

            # Allow embedded hyphens.
            "docker-rules/docker",

            # Allow multiple hyphens as well.
            "docker---rules/docker",

            # Username doc and image name docker being tested.
            "doc/docker",

            # single character names are now allowed.
            "d/docker",
            "jess/t",

            # Consecutive underscores.
            "dock__er/docker",
        ]
        invalid_repository_names = [
            # Disallow capital letters.
            "docker/Docker",

            # Only allow one slash.
            "docker///docker",

            # Disallow 64-character hexadecimal.
            "1a3f5e7d9c1b3a5f7e9d1c3b5a7f9e1d3c5b7a9f1e3d5d7c9b1a3f5e7d9c1b3a",

            # Disallow leading and trailing hyphens in namespace.
            "-docker/docker",
            "docker-/docker",
            "-docker-/docker",

            # Don't allow underscores everywhere (as opposed to hyphens).
            "____/____",

            "_docker/_docker",

            # Disallow consecutive periods.
            "dock..er/docker",
            "dock_.er/docker",
            "dock-.er/docker",

            # No repository.
            "docker/",

            # namespace too long
            "this_is_not_a_valid_namespace_because_its_lenth_is_greater_than_255_this_is_not_a_valid_namespace_because_its_lenth_is_greater_than_255_this_is_not_a_valid_namespace_because_its_lenth_is_greater_than_255_this_is_not_a_valid_namespace_because_its_lenth_is_greater_than_255/docker",
        ]

        for name in valid_repository_names:
            ref = reference.Reference.parse_normalized_named(name)
            self.assertIsNotNone(ref)

        for name in invalid_repository_names:
            self.assertRaises(reference.InvalidReference, reference.Reference.parse_normalized_named, name)
