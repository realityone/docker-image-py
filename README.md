# docker-image-py
Parse docker image as distribution does.

## Usage

### Install

You can install from PyPI.

```shell
$ pip install docker-image-py
```

Or install from GitHub for latest version.

```shell
$ pip install https://github.com/realityone/docker-image-py/archive/master.zip
```

### Parse Docker Image Names

For most user input, use `parse_normalized_named()`. This follows Docker CLI
rules for familiar names: it fills in `docker.io`, adds `library/` for official
images, and keeps custom registries intact.

```python
>>> from docker_image import reference
>>>
>>> ref = reference.Reference.parse_normalized_named('ubuntu')
>>> print(ref)
{'name': 'docker.io/library/ubuntu', 'tag': None, 'digest': None}
>>> print(ref.familiar_name())
ubuntu
>>> ref = reference.Reference.parse_normalized_named('containous/traefik')
>>> print(ref)
{'name': 'docker.io/containous/traefik', 'tag': None, 'digest': None}
>>> hostname, name = ref.split_hostname()
>>> print('hostname: {}, name: {}'.format(hostname, name))
hostname: docker.io, name: containous/traefik
>>> ref = reference.Reference.parse_normalized_named('daocloud.io/nginx:latest')
>>> print(ref)
{'name': 'daocloud.io/nginx', 'tag': 'latest', 'digest': None}

```

Do not use `parse()` for every image string. `parse()` is the raw syntax parser
from the distribution reference grammar; it does not infer Docker Hub defaults.
Use it when the input is already a literal reference and you want grammar-level
parsing only.

```python
>>> from docker_image import reference
>>>
>>> ref = reference.Reference.parse('nginx:latest')
>>> print(ref)
{'name': 'nginx', 'tag': 'latest', 'digest': None}
>>> ref = reference.Reference.parse('daocloud.io/nginx')
>>> print(ref)
{'name': 'daocloud.io/nginx', 'tag': None, 'digest': None}
>>> hostname, name = ref.split_hostname()
>>> print('hostname: {}, name: {}'.format(hostname, name))
hostname: daocloud.io, name: nginx
>>> ref = reference.Reference.parse(
...     'daocloud.io/nginx:1.11-alpine@sha256:14bf491df1d58404433b577e093c906460871ee677d18caa276d9c03727e0b33'
... )
>>> print(ref)
{'name': 'daocloud.io/nginx', 'tag': '1.11-alpine', 'digest': 'sha256:14bf491df1d58404433b577e093c906460871ee677d18caa276d9c03727e0b33'}

```

One common mistake is expecting raw `parse()` to apply Docker Hub namespace
rules. It does not:

```python
>>> from docker_image import reference
>>>
>>> raw = reference.Reference.parse('containous/traefik')
>>> raw.split_hostname()
('containous', 'traefik')
>>> normalized = reference.Reference.parse_normalized_named('containous/traefik')
>>> hostname, name = normalized.split_hostname()
>>> print('hostname: {}, name: {}'.format(hostname, name))
hostname: docker.io, name: containous/traefik

```

## Reference

- https://github.com/distribution/reference
