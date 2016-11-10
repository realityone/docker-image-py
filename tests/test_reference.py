import unittest

from docker_image import reference


class TestReference(unittest.TestCase):
    def test_reference(self):
        def create_reference_test_cases(input_, err=None, repository=None, hostname=None, tag=None, digest=None):
            return {
                'input': input_,
                'err': err,
                'repository': repository,
                'hostname': hostname,
                'tag': tag,
                'digest': digest,
            }

        name = 'daocloud.io/nginx:latest'
        r = reference.Reference.parse(name)
        a = r.split_hostname()
        self.assertEqual({
            'name': 'daocloud.io/nginx',
            'tag': 'latest',
            'digest': None
        }, r)
