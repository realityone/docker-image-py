import unittest

from docker_image import digest
from docker_image import reference


class TestReference(unittest.TestCase):
    def test_reference(self):
        def create_test_case(input_, err=None, repository=None, hostname=None, tag=None, digest=None):
            return {
                'input': input_,
                'err': err,
                'repository': repository,
                'hostname': hostname,
                'tag': tag,
                'digest': digest,
            }

        test_cases = [
            create_test_case(input_='test_com', repository='test_com'),
            create_test_case(input_='test.com:tag', repository='test.com', tag='tag'),
            create_test_case(input_='test.com:5000', repository='test.com', tag='5000'),
            create_test_case(input_='test.com/repo:tag', repository='test.com/repo', hostname='test.com', tag='tag'),
            create_test_case(input_='test:5000/repo', repository='test:5000/repo', hostname='test:5000'),
            create_test_case(input_='test:5000/repo:tag', repository='test:5000/repo', hostname='test:5000', tag='tag'),
            create_test_case(input_='test:5000/repo@sha256:{}'.format('f' * 64),
                             repository='test:5000/repo', hostname='test:5000', digest='sha256:{}'.format('f' * 64)),
            create_test_case(input_='test:5000/repo:tag@sha256:{}'.format('f' * 64),
                             repository='test:5000/repo', hostname='test:5000', tag='tag', digest='sha256:{}'.format('f' * 64)),
            create_test_case(input_='test:5000/repo', repository='test:5000/repo', hostname='test:5000'),
            create_test_case(input_='', err=reference.NameEmpty),
            create_test_case(input_=':justtag', err=reference.ReferenceInvalidFormat),
            create_test_case(input_='@sha256:{}'.format('f' * 64), err=reference.ReferenceInvalidFormat),
            create_test_case(input_='repo@sha256:{}'.format('f' * 34), err=digest.DigestInvalidLength),
            create_test_case(input_='validname@invaliddigest:{}'.format('f' * 64), err=digest.DigestUnsupported),
            create_test_case(input_='{}a:tag'.format('a/' * 128), err=reference.NameTooLong),
            create_test_case(input_='{}a:tag-puts-this-over-max'.format('a/' * 127), repository='{}a'.format('a/' * 127),
                             hostname='a', tag='tag-puts-this-over-max'),
            create_test_case(input_='aa/asdf$$^/aa', err=reference.ReferenceInvalidFormat),
            create_test_case(input_='sub-dom1.foo.com/bar/baz/quux', repository='sub-dom1.foo.com/bar/baz/quux',
                             hostname='sub-dom1.foo.com'),
            create_test_case(input_='sub-dom1.foo.com/bar/baz/quux:some-long-tag', repository='sub-dom1.foo.com/bar/baz/quux',
                             hostname='sub-dom1.foo.com', tag='some-long-tag'),
            create_test_case(input_='b.gcr.io/test.example.com/my-app:test.example.com',
                             repository='b.gcr.io/test.example.com/my-app', hostname='b.gcr.io', tag='test.example.com'),
            create_test_case(input_='xn--n3h.com/myimage:xn--n3h.com', repository='xn--n3h.com/myimage', hostname='xn--n3h.com',
                             tag='xn--n3h.com'),
            create_test_case(input_='xn--7o8h.com/myimage:xn--7o8h.com@sha512:{}'.format('f' * 128),
                             repository='xn--7o8h.com/myimage', hostname='xn--7o8h.com', tag='xn--7o8h.com',
                             digest='sha512:{}'.format('f' * 128)),
            create_test_case(input_='foo_bar.com:8080', repository='foo_bar.com', tag='8080'),
            create_test_case(input_='foo/foo_bar.com:8080', repository='foo/foo_bar.com', hostname='foo', tag='8080'),
            create_test_case(input_='123.dkr.ecr.eu-west-1.amazonaws.com:lol/abc:d', err=reference.ReferenceInvalidFormat),
            create_test_case(input_='docker.artifactory.us.foo.mycompany.com/bar/node?18', err=reference.ReferenceInvalidFormat),
        ]

        for tc in test_cases:
            if tc['err']:
                self.assertRaises(tc['err'], reference.Reference.parse, tc['input'])
                continue

            try:
                r = reference.Reference.parse(tc['input'])
            except Exception as e:
                raise e
            else:
                if tc['repository']:
                    self.assertEqual(tc['repository'], r['name'])

                if tc['hostname']:
                    hostname, _ = r.split_hostname()
                    self.assertEqual(tc['hostname'], hostname)

                if tc['tag']:
                    self.assertEqual(tc['tag'], r['tag'])

                if tc['digest']:
                    self.assertEqual(tc['digest'], r['digest'])


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
            create_test_case('fooo/bar', 'fooo/bar', 'docker.io/fooo/bar', 'index.docker.io/fooo/bar', 'docker.io'),
            create_test_case('library/ubuntu', 'ubuntu', 'docker.io/library/ubuntu', 'library/ubuntu', 'docker.io'),
            create_test_case('nonlibrary/ubuntu', 'nonlibrary/ubuntu', 'docker.io/nonlibrary/ubuntu', '', 'docker.io'),
            create_test_case('other/library', 'other/library', 'docker.io/other/library', '', 'docker.io'),
            create_test_case('private/moonbase', '127.0.0.1:8000/private/moonbase', '127.0.0.1:8000/private/moonbase', '',
                             '127.0.0.1:8000'),
            create_test_case('privatebase', '127.0.0.1:8000/privatebase', '127.0.0.1:8000/privatebase', '', '127.0.0.1:8000'),
            create_test_case('private/moonbase', 'example.com/private/moonbase', 'example.com/private/moonbase', '',
                             'example.com'),
            create_test_case('privatebase', 'example.com/privatebase', 'example.com/privatebase', '', 'example.com'),
            create_test_case('private/moonbase', 'example.com:8000/private/moonbase', 'example.com:8000/private/moonbase', '',
                             'example.com:8000'),
            create_test_case('privatebasee', 'example.com:8000/privatebasee', 'example.com:8000/privatebasee', '',
                             'example.com:8000'),
            create_test_case('library/ubuntu-12.04-base', 'ubuntu-12.04-base', 'docker.io/library/ubuntu-12.04-base',
                             'index.docker.io/library/ubuntu-12.04-base', 'docker.io'),
            create_test_case('library/foo', 'foo', 'docker.io/library/foo', 'docker.io/foo', 'docker.io'),
            create_test_case('library/foo/bar', 'library/foo/bar', 'docker.io/library/foo/bar', '', 'docker.io'),
            create_test_case('store/foo/bar', 'store/foo/bar', 'docker.io/store/foo/bar', '', 'docker.io'),
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
            "docker.io/docker/docker",
            "docker.io/library/debian",
            "docker.io/debian",
            "index.docker.io/docker/docker",
            "index.docker.io/library/debian",
            "index.docker.io/debian",
            "127.0.0.1:5000/docker/docker",
            "127.0.0.1:5000/library/debian",
            "127.0.0.1:5000/debian",
            "thisisthesongthatneverendsitgoesonandonandonthisisthesongthatnev",

            # This test case was moved from invalid to valid since it is valid input
            # when specified with a hostname, it removes the ambiguity from about
            # whether the value is an identifier or repository name
            "docker.io/1a3f5e7d9c1b3a5f7e9d1c3b5a7f9e1d3c5b7a9f1e3d5d7c9b1a3f5e7d9c1b3a",
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
            "1a3f5e7d9c1b3a5f7e9d1c3b5a7f9e1d3c5b7a9f1e3d5d7c9b1a3f5e7d9c1b3a",
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
