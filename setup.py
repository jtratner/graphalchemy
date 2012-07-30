try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Basic Node/Edge model for SQLAlchemy',
    'author': 'Jeffrey Tratner',
    'url': 'jeffreytratner.com',
    'download_url': 'Where to download it.',
    'author_email': 'jeffrey.tratner@gmail.com',
    'version': '0.1',
    'install_requires': ['SQLAlchemy>=0.7','nose'],
    'packages': ['graphalchemy'],
    'scripts': [],
    'name': 'graphalchemy'
}

setup(**config)
