from setuptools import setup, find_packages
from wandbfs import __version__

setup(
    name='wandbfs',
    version=__version__,
    packages=find_packages(include=('wandbfs', 'wandbfs.*')),
    author='Jonáš Kulhánek',
    author_email='jonas.kulhanek@live.com',
    license='MIT License',
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    url='https://github.com/jkulhanek/wandbfs',
    install_requires=[x.rstrip('\n') for x in open('requirements.txt')],
    entry_points={
        'fsspec.specs': [
            'wandb=wandbfs.WandbFS',
        ],
    })
