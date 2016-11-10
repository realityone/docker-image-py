import unittest

from docker_image import reference


class TestReference(unittest.TestCase):
    def test_reference(self):
        name = 'daocloud.io/nginx:latest'
        r = reference.Reference.parse(name)
        self.assertEqual({
            'name': 'daocloud.io/nginx',
            'tag': 'latest',
            'digest': None
        }, r)
