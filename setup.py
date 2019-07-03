import os

from setuptools import setup, find_packages
import virtualenvconfig

name = 'virtualenvconfig'
dirname = os.path.dirname(os.path.abspath(__file__))

# Get the long description from the README file.
with open(os.path.join(dirname, 'README.md')) as fle:
    long_description = fle.read()

setup(
    name=name,
    version=virtualenvconfig.__version__,
    description=r'Customize abi resolution for a given virtualenv setup.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/blurstudio/{}'.format(name),
    download_url='https://github.com/blurstudio/{}/archive/master.zip'.format(name),
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
      'gorilla',
    ],
    author_email='pipeline@blur.com'
)
