from setuptools import setup, find_packages

setup(
    name='conx',
    version='1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    package_data={
        'conx': ['settings.json'],  # Include settings.json
    },
    scripts=['bin/conx'],
    author='Charlie Tulip',
    author_email='charlietulip117@gmail.com',
    description='A simple Python-based package manager',
    install_requires=[
        'requests',  # Add the requests dependency
    ],
)
