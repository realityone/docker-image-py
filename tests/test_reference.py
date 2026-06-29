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
            create_test_case(input_='repo@sha256:{}'.format('F' * 64), err=digest.InvalidDigest),
            create_test_case(input_='repo@SHA256:{}'.format('f' * 64), err=digest.InvalidDigest),
            create_test_case(input_='validname@invaliddigest:{}'.format('f' * 64), err=digest.DigestUnsupported),
            create_test_case(input_='Uppercase:tag', err=reference.NameContainsUppercase),
            create_test_case(input_='test:5000/Uppercase/lowercase:tag', err=reference.NameContainsUppercase),
            create_test_case(input_='lowercase:Uppercase', repository='lowercase', tag='Uppercase'),
            create_test_case(input_='domain/{}:tag'.format('a' * 256), err=reference.NameTooLong),
            create_test_case(input_='{}a:tag'.format('a/' * 128), repository='{}a'.format('a/' * 128),
                             hostname='a', tag='tag'),
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
            create_test_case(input_='192.168.1.1', repository='192.168.1.1'),
            create_test_case(input_='192.168.1.1:tag', repository='192.168.1.1', tag='tag'),
            create_test_case(input_='192.168.1.1:5000', repository='192.168.1.1', tag='5000'),
            create_test_case(input_='192.168.1.1/repo', repository='192.168.1.1/repo', hostname='192.168.1.1'),
            create_test_case(input_='192.168.1.1:5000/repo', repository='192.168.1.1:5000/repo',
                             hostname='192.168.1.1:5000'),
            create_test_case(input_='192.168.1.1:5000/repo:5050', repository='192.168.1.1:5000/repo',
                             hostname='192.168.1.1:5000', tag='5050'),
            create_test_case(input_='[2001:db8::1]', err=reference.ReferenceInvalidFormat),
            create_test_case(input_='[2001:db8::1]:5000', err=reference.ReferenceInvalidFormat),
            create_test_case(input_='[2001:db8::1]:tag', err=reference.ReferenceInvalidFormat),
            create_test_case(input_='[2001:db8::1]/repo', repository='[2001:db8::1]/repo', hostname='[2001:db8::1]'),
            create_test_case(input_='[2001:db8:1:2:3:4:5:6]/repo:tag',
                             repository='[2001:db8:1:2:3:4:5:6]/repo',
                             hostname='[2001:db8:1:2:3:4:5:6]', tag='tag'),
            create_test_case(input_='[2001:db8::1]:5000/repo',
                             repository='[2001:db8::1]:5000/repo', hostname='[2001:db8::1]:5000'),
            create_test_case(input_='[2001:db8::1]:5000/repo:tag',
                             repository='[2001:db8::1]:5000/repo',
                             hostname='[2001:db8::1]:5000', tag='tag'),
            create_test_case(input_='[2001:db8::1]:5000/repo@sha256:{}'.format('f' * 64),
                             repository='[2001:db8::1]:5000/repo', hostname='[2001:db8::1]:5000',
                             digest='sha256:{}'.format('f' * 64)),
            create_test_case(input_='[2001:db8::1]:5000/repo:tag@sha256:{}'.format('f' * 64),
                             repository='[2001:db8::1]:5000/repo', hostname='[2001:db8::1]:5000', tag='tag',
                             digest='sha256:{}'.format('f' * 64)),
            create_test_case(input_='[2001:db8::]:5000/repo',
                             repository='[2001:db8::]:5000/repo', hostname='[2001:db8::]:5000'),
            create_test_case(input_='[::1]:5000/repo', repository='[::1]:5000/repo', hostname='[::1]:5000'),
            create_test_case(input_='[fe80::1%eth0]:5000/repo', err=reference.ReferenceInvalidFormat),
            create_test_case(input_='[fe80::1%@invalidzone]:5000/repo', err=reference.ReferenceInvalidFormat),
            create_test_case(input_='example.com/{}:tag'.format('a' * 255),
                             repository='example.com/{}'.format('a' * 255), hostname='example.com', tag='tag'),
            create_test_case(input_='example.com/{}'.format('a' * 256), err=reference.NameTooLong),
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
