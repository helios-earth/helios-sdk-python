from setuptools import find_packages
from setuptools import setup

import helios

__version__ = helios.__version__

setup(name='Helios',
      version=__version__,
      description='Use the Helios APIs in Python',
      author='Michael Bayer',
      author_email='mbayer@harris.com',
      url='https://github.com/harris-helios/helios-sdk-python',
      download_url='https://github.com/harris-helios/'
                   'helios-sdk-python/archive/{}.tar.gz'.format(__version__),
      license='MIT',
      install_requires=['requests',
                        'numpy',
                        'Pillow',
                        'python_dateutil'],
      extras_require={
          'tests': ['pytest'],
      },
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      packages=find_packages())
