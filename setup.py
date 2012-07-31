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
    'version': '0.1.0',
    'install_requires': ['SQLAlchemy>=0.7','nose'],
    'packages': ['graphalchemy'],
    'scripts': [],
    'name': 'GraphAlchemy',
    'license': 'MIT License',
    'long_description':open("README.rst").read(),
    'classifiers': [
        "Topic :: Database :: Front-Ends",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering :: Information Analysis",
        ],
}

setup(**config)
