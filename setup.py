from distutils.core import setup

DISTNAME='hansel'
FULLVERSION='0.1'

setup(
    name=DISTNAME,
    version=FULLVERSION,
    packages=['hansel'],
    install_requires = [
        'astor',
        'asttools'
        'earthdragon',
        'six',
    ]
)
