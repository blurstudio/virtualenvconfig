import os

from setuptools import setup, find_packages
from pillar.version import Version

name = 'virtualenvconfig'
dirname = os.path.dirname(os.path.abspath(__file__))
version = Version(dirname, name)

# Get the long description from the README file.
with open(os.path.join(dirname, 'README.md')) as fle:
    long_description = fle.read()

setup(
    name=name,
    version=version.get_version_string(),
    description=r'{PACKAGE_DESCRIPTION}',
    long_description=long_description,
    url='https://gitlab.blur.com/pipeline/{}.git'.format(name),
    download_url='https://gitlab.blur.com/pipeline/{}/repository/archive.tar.gz?ref=master'.format(name),
    license='GNU LGPLv3',
    classifiers=[
           'Development Status :: 3 - Alpha',
           'Intended Audience :: Developers',
           'Programming Language :: Python',
           'Programming Language :: Python :: 2',
           'Programming Language :: Python :: 2.7',
           'Programming Language :: Python :: Implementation :: CPython',
           'Programming Language :: Python :: Implementation :: PyPy',
           'Operating System :: OS Independent',
           'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
    ],
    keywords='',
    py_modules=["virtualenvconfig"],
    include_package_data=True,
    author='Blur Studio',
    install_requires=[
      'blur-pillar>=0.3.0',
      'gorilla',
    ],
    author_email='pipeline@blur.com'
)