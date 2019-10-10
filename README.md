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

### Parse Docker Image

```python
>>> from docker_image import reference
>>> 
>>> # with registry, repo, tag, and digest
>>> ref = reference.Reference.parse(
...     'daocloud.io/nginx:1.11-alpine@sha256:14bf491df1d58404433b577e093c906460871ee677d18caa276d9c03727e0b33'
... )
>>> print ref
{'tag': '1.11-alpine', 'name': 'daocloud.io/nginx', 'digest': 'sha256:14bf491df1d58404433b577e093c906460871ee677d18caa276d9c03727e0b33'}
>>> 
>>> # with registry and repo
>>> ref = reference.Reference.parse(
...     'daocloud.io/nginx'
... )
>>> print ref
{'tag': None, 'name': 'daocloud.io/nginx', 'digest': None}
>>> # get registry hostname
>>> hostname, name = ref.split_hostname()
>>> print 'hostname: {}, name: {}'.format(hostname, name)
hostname: daocloud.io, name: nginx
>>> # with registry, repo and tag
>>> ref = reference.Reference.parse(
...     'daocloud.io/nginx:latest'
... )
>>> print ref
{'tag': 'latest', 'name': 'daocloud.io/nginx', 'digest': None}
>>> # with repo and tag
>>> ref = reference.Reference.parse(
...     'nginx:latest'
... )
>>> print ref
{'tag': 'latest', 'name': 'nginx', 'digest': None}
>>> # only repo
>>> ref = reference.Reference.parse(
...     'nginx'
... )
>>> print ref
{'tag': None, 'name': 'nginx', 'digest': None}
>>> ref = reference.Reference.parse_normalized_named(
...     'containous/traefik'
... )
>>> print ref
{'name': 'docker.io/containous/traefik', 'tag': None, 'digest': None}
>>> hostname, name = ref.split_hostname()
>>> print 'hostname: {}, name: {}'.format(hostname, name)
hostname: docker.io, name: containous/traefik
```

## Reference

- https://github.com/docker/distribution/tree/master/reference