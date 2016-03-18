try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Pathway reconstruction from meta-genomes',
    'author': 'Dylan Storey',
    'url': 'www.github.com/magrid',
    'download_url': '',
    'author_email': 'dylan.storey@gmail.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['magrid'],
    'scripts': [],
    'name': 'magrid'
}

setup(**config)
